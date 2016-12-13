# coding=utf8

import sys
from txt2mobi.scaffold import init_project, generate_project, test_project


def main():
    commands = ['init', 'gen', 'test', 'help']
    if len(sys.argv) < 2:
        print "Missing argument! Arguments must be [ %s ]" % "  ".join(commands)
        sys.exit(1)
    command = sys.argv[1]
    if command not in commands:
        print "Wrong argument! Arguments must be [ %s ]" % "  ".join(commands)
        sys.exit(1)
    if command == commands[0]:
        init_project()
        print 'project init successfull!'
        sys.exit(0)
    if command == commands[1]:
        generate_project()
        print 'project generated successfull!'
        sys.exit(0)
    if command == commands[2]:
        test_project()
        print 'project test successfull!'
        sys.exit(0)
    if command == commands[3]:
        print '----help end----'
        sys.exit(0)


if __name__ == "__main__":
    main()
