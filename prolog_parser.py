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
    ARROW = lit('->')
    VAR = reg(r'[A-Z][a-zA-Z_0-9]*') > named_print('variable')
    ID = pred(reg(r'[a-z_][a-zA-Z_0-9]*'), no_match(KEYWORD.parse), 'ID') > named_print('ID')

    module = (MODULE & ID & DOT > (lambda x: "MODULE " + x[1])) | lit('')

    atom = (atom_args > (lambda x: 'atom (' + x + ')')) | ID
    atom_args = (ID & rep1(atom_brackets | VAR | ID)) > (lambda x: x[0] + ' ' + ' '.join(x[1]))
    atom_brackets = (atom | VAR > join_list) | (LBR & atom_brackets & RBR > (lambda x: join_list(x[1])))

    T = (LBR & body & RBR) | atom > join_list
    M = ((T & COMMA & M) > (lambda x: '(conjunction ' + x[0] + ' ' + x[2] + ')')) | (T > join_list)
    body = ((M & SEMICOLON & body) > (lambda x: '(disjunction ' + x[0] + ' ' + x[2] + ')')) | (M > join_list)

    rel_no_body = (atom & DOT) > (lambda x: 'relation ' + 'head ' + x[0])
    rel_body = ((atom & CORK & body & DOT) > (lambda x: 'relation ' + 'head ' + x[0] + ' body ' + x[2]))
    relation = rel_no_body | rel_body

    type_seq = TYPE
    typedef = TYPE

    program = (module & (rep(relation) > newline)) > newline


def parse(s, args):
    if '--atom' in args:
        return PrologParser.atom.parse(s)
    elif '--typeexpr' in args:
        return PrologParser.type_seq.parse(s)
    elif '--type' in args:
        return PrologParser.typedef.parse(s)
    elif '--module' in args:
        return PrologParser.module.parse(s)
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
        if type(result) == Success:
            print(result.value, file=open(filename + '.out', 'w'))
        else:
            print(result.message)


if __name__ == '__main__':
    main(sys.argv[1:])
