# coding=utf8

import chardet
import re
from txt2mobi.utilities import codeTrans, ProjectConfig, no_html


config = ProjectConfig()

allowed = [u',', u'.', u"!", u"?", u":", u"*", u"[", u"]", u";", u"-", u"_", u"。", u"，", u"?", u"：",
           u"；", u"【", u"】", u" ", u""]

english = u'qazxswedcvfrtgbnhyujmkiolpQAZXSWEDCVFRTGBNHYUJMKIOLP1234567890'

def get_coding(file_content):
    print(file_content)
    return 'utf-8'


def clear_line(line):
    """
    去掉特殊符号
    :param line:
    :type line:
    :return:
    :rtype:
    """
    wd = [w for w in line if (19968 <= ord(w) <= 40869) or (w in allowed) or (w in english)]
    result_line = u"".join(wd)
    return result_line


def unicode_line(file_content):
    print ("正在识别文件字符集...")
    coding = codeTrans(get_coding(file_content[:500]))
    print ("文件字符集:", coding)
    lines = file_content.split('\n')
    result_lines = []
    error_lines = 0
    for idx, line in enumerate(lines):
        try:
            result_lines.append(clear_line(line))
        except Exception as e:
            error_lines += 1
    if error_lines:
        print (u"有%s行无法解析" % error_lines)
    return result_lines


class Chapter(object):
    """
    章节对象
    """
    def __init__(self, title, idx):
        self.title = title
        self.lines = []
        self.idx = idx

    def append_line(self, line):
        line = no_html(line)
        line = line.replace('\r', '').replace('\n', '').replace('<', '&lt;').replace('>', '&gt;')
        self.lines.append(line)

    def as_html(self):
        if len(self.lines) < 1:
            return ""
        rows = ["    <a name=\"ch%s\"/><h3 id=\"ch%s\">%s</h3>" % (self.idx, self.idx, self.title)]
        for line in self.lines:
            rows.append("    <p>%s</p>" % line)
        rows.append("    <mbp:pagebreak />")
        print ("章节", self.title, "生成完毕")
        return "\n".join(rows)

    def as_ncx(self, idx):
        if len(self.lines) < 1:
            return ""
        ncx = """      <navPoint id="ch%(idx)s" playOrder="%(idx)s">
            <navLabel>
                <text>
                    %(title)s
                </text>
            </navLabel>
            <content src="book-%(book_idx)s.html#ch%(idx)s" />
        </navPoint>""" % dict(idx=self.idx, title=self.title, book_idx=idx)
        print ("章节索引", self.title, "生成完毕")
        return ncx


class Book(object):
    """
    书对象
    """
    def __init__(self, file_path, title_filter):
        with open(file_path, 'r') as f:
            lines = unicode_line(f.read())
            f.close()
        self.title_filter = title_filter
        self.chapters = []
        self.process_lines(lines)
        self.name = config.title

    def trim(self):
        """
        去掉没有内容的章节
        :return:
        :rtype:
        """
        trimed_chapters = [chapter for chapter in self.chapters if chapter.lines]
        del self.chapters[:]
        self.chapters = trimed_chapters

    def book_count(self):
        """
        计算有几本书,因为太大了生成出来的文件有问题, 所以每1500章就切分生成一个mobi文件
        :return:
        :rtype:
        """
        ct = len(self.chapters) // int(config.max_chapter)
        md = len(self.chapters) // int(config.max_chapter)
        if md > 0:
            ct += 1
        if ct + md == 0:
            ct = 1
        return ct

    def __start_end_of_index(self, idx):
        """
        根据idx计算开始和结束的id
        :param idx:
        :type idx:
        :return:
        :rtype:
        """
        start = (idx - 1) * int(config.max_chapter)
        end = idx * int(config.max_chapter)
        return start, end

    def __is_chapter_title(self, line):
        """
        检测是否章节标题
        :param line:
        :type line:
        :return:
        :rtype:
        """
        if self.title_filter:
            strip_line = line.strip()
            if 3 < len(strip_line) < 30:
                if re.match(self.title_filter, strip_line):
                    return True
        else:
            if line.strip().startswith(u'第'):
                if 3 < len(line.strip()) < 30 and u"第" in line and u"章" in line:
                    return True
            if line.strip().startswith(u'第'):
                if 3 < len(line.strip()) < 30 and u"第" in line and u"张" in line:
                    return True
            if line.strip().startswith(u'正文 第'):
                if 3 < len(line.strip()) < 30 and u"第" in line and u"章" in line:
                    return True
            line = line.replace(u"．", u".").replace(u":", u".")
            if line.split('.')[0].isdigit():
                if 3 < len(line.strip()) < 20:
                    return True
            if len(line) < 20 and (line.strip()[:3].isdigit() or line.strip()[:4].isdigit()):
                return True
            if len(line) < 40 and u"第" in line and u"卷" in line:
                if line[line.index(u"第") + 1: line.index(u"卷")] in [u"一", u"二", u"三", u"四", u"五", u"六", u"七", u"八", u"九", u"十"]:
                    return True
            if line.strip().startswith(u'[第'):
                if 3 < len(line.strip()) < 30 and u"第" in line and u"章" in line:
                    return True

        return False

    def process_lines(self, lines):
        """
        循环处理所有的行
        :param lines:
        :type lines:
        :return:
        :rtype:
        """
        idx = 1
        chapter = Chapter("前言", 0)
        self.chapters.append(chapter)
        for line in lines:
            if self.__is_chapter_title(line):
                chapter = Chapter(line.strip(), idx)
                self.chapters.append(chapter)
                idx+=1
            else:
                if len(line.strip()):
                    chapter.append_line(line)

    def gen_menu(self, idx):
        """
        生成目录html
        :return:
        :rtype:
        """
        start, end = self.__start_end_of_index(idx)
        menu_base = """
    <div id="toc">
        <h2>
            目录<br />
        </h2>
        <ul>
%s
        </ul>
    </div>
    <div class="pagebreak"></div>
        """ % "\n".join(["            <li><a href=\"#ch%s\">%s</a></li>" % (
            chapter.idx,
            chapter.title) for chapter in self.chapters[start: end] if chapter.lines])
        return menu_base

    def gen_html_file(self, idx):
        """
        生成HTML文件
        :return:
        :rtype:
        """
        menu = self.gen_menu(idx)
        start, end = self.__start_end_of_index(idx)
        book_name = config.title
        contents = "\n".join([chapter.as_html() for chapter in self. chapters[start: end]])

        data = dict(book_name=book_name, menu=menu, content=contents)

        html_base = """<!DOCTYPE html
PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="zh" xml:lang="zh">
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
    <title>%(book_name)s</title>
    <style type="text/css">
    p { margin-top: 1em; text-indent: 0em; }
    h1 {margin-top: 1em}
    h2 {margin: 2em 0 1em; text-align: center; font-size: 2.5em;}
    h3 {margin: 0 0 2em; font-weight: normal; text-align:center; font-size: 1.5em; font-style: italic;}
    .center { text-align: center; }
    .pagebreak { page-break-before: always; }
    </style>
</head>
<body>
<a name="toc"/>
%(menu)s
<!-- Your book goes here -->
%(content)s
</body>
</html>
        """ % data
        return html_base

    def gen_ncx(self, idx):
        """
        生成NCX文件内容
        :return:
        :rtype:
        """
        start, end = self.__start_end_of_index(idx)
        data = dict(
            book_name=config.title,
            menavPoints="\n".join([chapter.as_ncx(idx) for chapter in self.chapters[start: end]])
        )
        ncx_base = """<?xml version="1.0"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"
 "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
 <head>
 </head>
        <docTitle>
               <text>%(book_name)s</text>
        </docTitle>
    <navMap>
        %(menavPoints)s
    </navMap>
</ncx>
        """ % data
        return ncx_base

    def gen_opf_file(self, idx):
        """
        生成项目文件
        :return:
        :rtype:
        """
        opf_file = """<?xml version="1.0" encoding="utf-8"?>
<package unique-identifier="uid" xmlns:opf="http://www.idpf.org/2007/opf" xmlns:asd="http://www.idpf.org/asdfaf">
    <metadata>
        <dc-metadata  xmlns:dc="http://purl.org/metadata/dublin_core" xmlns:oebpackage="http://openebook.org/namespaces/oeb-package/1.0/">
            <dc:Title>%(title)s-%(idx)s</dc:Title>
            <dc:Language>zh-cn</dc:Language>
            <dc:Creator>%(author)s</dc:Creator>
            <dc:Copyrights>%(author)s</dc:Copyrights>
            <dc:Publisher>Alexander.Li</dc:Publisher>
            <x-metadata>
                <EmbeddedCover>%(cover)s</EmbeddedCover>
            </x-metadata>
        </dc-metadata>
    </metadata>
    <manifest>
        <item id="toc" properties="nav" href="book-%(idx)s.html" media-type="application/xhtml+xml"/>
        <item id="content" media-type="application/xhtml+xml" href="book-%(idx)s.html"></item>
        <item id="cover-image" media-type="image/png" href="%(cover)s"/>
        <item id="ncx" media-type="application/x-dtbncx+xml" href="toc-%(idx)s.ncx"/>
    </manifest>
    <spine toc="ncx">
        <itemref idref="cover-image"/>
        <itemref idref="toc"/>
        <itemref idref="content"/>
    </spine>
    <guide>
        <reference type="toc" title="%(title_name)s" href="book-%(idx)s.html#toc"/>
        <reference type="content" title="Book" href="book-%(idx)s.html"/>
    </guide>
</package>
        """ % dict(
            title_name=u"目录",
            author=config.author,
            title="%s-%s" % (config.title, idx) if self.book_count() > 1 else config.title,
            cover=config.cover_image,
            idx="%s" % idx
        )
        return opf_file

    def gen_command(self, idx):
        """
        生成执行的命令
        :param idx:
        :type idx:
        :return:
        :rtype:
        """
        return "%s project-%s.opf" % (config.gen_command, idx)
