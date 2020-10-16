#!/usr/bin/env python3
from parsita import *
import sys


def no_match(f):
    return lambda x: not type(f(x)) == Success


def named_print(name):
    return lambda x: '(' + name + ' ' + x + ')'


def join_list(x, sep=''):
    return sep.join(x)


def newline(x):
    return join_list(x, '\n')


class PrologParser(TextParsers, whitespace=r'[ \t\n]*'):
    MODULE = lit('module')
    TYPE = lit('type')
    KEYWORD = MODULE | TYPE

    DOT = lit('.')
    CORK = lit(':-')
    SEMICOLON = lit(';')
    COMMA = lit(',')
    LBR = lit('(')
    RBR = lit(')')
    LBRSQ = lit('[')
    RBRSQ = lit(']')
    VBAR = lit('|')
    ARROW = lit('->')
    VAR = reg(r'[A-Z][a-zA-Z_0-9]*') > named_print('variable')
    ID = pred(reg(r'[a-z_][a-zA-Z_0-9]*'), no_match(KEYWORD.parse), 'ID') > named_print('ID')

    module = (MODULE & ID & DOT > (lambda x: "MODULE " + x[1])) | lit('')

    atom = (atom_args > (lambda x: 'atom (' + x + ')')) | ID
    atom_args = (ID & rep1(atom_brackets | VAR | ID | LIST)) > (lambda x: x[0] + ' ' + ' '.join(x[1]))
    atom_brackets = (atom | VAR > join_list) | (LBR & atom_brackets & RBR > (lambda x: join_list(x[1])))

    T = (LBR & body & RBR) | atom > join_list
    M = ((T & COMMA & M) > (lambda x: '(conjunction ' + x[0] + ' ' + x[2] + ')')) | (T > join_list)
    body = ((M & SEMICOLON & body) > (lambda x: '(disjunction ' + x[0] + ' ' + x[2] + ')')) | (M > join_list)

    rel_no_body = (atom & DOT) > (lambda x: 'relation ' + 'head ' + x[0])
    rel_body = ((atom & CORK & body & DOT) > (lambda x: 'relation ' + 'head ' + x[0] + ' body ' + x[2]))
    relation = rel_no_body | rel_body

    typeseq_brackets = (LBR & typeseq & RBR) > join_list
    typeseq = rep1sep(atom | VAR | typeseq_brackets, ARROW) > (lambda x: ' -> '.join(x))
    typedef = (TYPE & ID & typeseq << DOT) > (lambda x: 'typedef ' + x[1] + ' (' + x[2] + ')')

    LIST_ENUM = (LBRSQ >> repsep(atom | VAR | LIST, COMMA) << RBRSQ) > (lambda x: '[' + ', '.join(x) + ']')
    LIST_HEAD_TAIL = (LBRSQ >> (atom | VAR | LIST) << VBAR & (VAR | LIST) << RBRSQ) > (lambda x: '[' + x[0] + ' | ' + x[1] + ']')
    LIST = LIST_ENUM | LIST_HEAD_TAIL

    program = (module & (rep(typedef) > newline) & (rep(relation) > newline)) > (lambda x: newline(filter(None, x)))


def parse(s, args):
    if '--atom' in args:
        return PrologParser.atom.parse(s)
    elif '--typeexpr' in args:
        return PrologParser.typeseq.parse(s)
    elif '--type' in args:
        return PrologParser.typedef.parse(s)
    elif '--module' in args:
        return PrologParser.module.parse(s)
    elif '--list' in args:
        return PrologParser.LIST.parse(s)
    elif '--relation' in args:
        return PrologParser.relation.parse(s)
    elif '--prog' in args:
        return PrologParser.program.parse(s)
    else:
        return PrologParser.program.parse(s)


def main(args):
    filename = args[-1]
    with open(filename, 'r') as file:
        result = parse(file.read(), args)
        out = sys.stdout if 'test' in args else open(filename + '.out', 'w')
        if type(result) == Success:
            print(result.value, file=out)
        else:
            print(result.message)  # put file=out here if you want errors to appear in .out file


if __name__ == '__main__':
    main(sys.argv[1:])
