#!/usr/bin/env python3
import prolog_parser
import re
from prolog_parser import PrologParser
from parsita import *


# test integrate


def test_integrate_correct(tmp_path, monkeypatch, capsys):
    inputs = ['module test.',
              'module test. type t f -> o.',
              'module test. type t f -> o. type t f -> o.',
              'module test. type t f -> o. type t f -> o. f :- name.',
              'module test. type t f -> o. type t f -> o. f :- name. a (b c) :- x, y, z.',
              'type t f -> o. type t f -> o. f :- name. a (b c) :- x, y, z.',
              'type t f -> o. f :- name. a (b c) :- x, y, z.',
              'f :- name. a (b c) :- x, y, z.',
              'a (b c) :- x, y, z.',
              'f.       \n\n\n\n  f :- g.      \n '
              '         f \n    :-   g, \n\n\nh   ; t  . '
              '   \n\n\n']

    outputs = ['MODULE (ID test)\n',
               'MODULE (ID test)\ntypedef (ID t) ((ID f) -> (ID o))\n',
               'MODULE (ID test)\ntypedef (ID t) ((ID f) -> (ID o))\ntypedef (ID t) ((ID f) -> (ID o))\n',
               'MODULE (ID test)\ntypedef (ID t) ((ID f) -> (ID o))\ntypedef (ID t) ((ID f) -> (ID o))\nrelation head '
               '(ID f) body (ID name)\n',
               'MODULE (ID test)\ntypedef (ID t) ((ID f) -> (ID o))\ntypedef (ID t) ((ID f) -> (ID o))\nrelation head '
               '(ID f) body (ID name)\nrelation head atom ((ID a) atom ((ID b) (ID c))) body (conjunction (ID x) ('
               'conjunction (ID y) (ID z)))\n',
               'typedef (ID t) ((ID f) -> (ID o))\ntypedef (ID t) ((ID f) -> (ID o))\nrelation head (ID f) body (ID '
               'name)\nrelation head atom ((ID a) atom ((ID b) (ID c))) body (conjunction (ID x) (conjunction (ID y) '
               '(ID z)))\n',
               'typedef (ID t) ((ID f) -> (ID o))\nrelation head (ID f) body (ID name)\nrelation head atom ((ID a) '
               'atom ((ID b) (ID c))) body (conjunction (ID x) (conjunction (ID y) (ID z)))\n',
               'relation head (ID f) body (ID name)\nrelation head atom ((ID a) atom ((ID b) (ID c))) body ('
               'conjunction (ID x) (conjunction (ID y) (ID z)))\n',
               'relation head atom ((ID a) atom ((ID b) (ID c))) body (conjunction (ID x) (conjunction (ID y) (ID '
               'z)))\n',
               'relation head (ID f)\nrelation head (ID f) body (ID g)\nrelation head (ID f) body (disjunction ('
               'conjunction (ID g) (ID h)) (ID t))\n']

    assert len(inputs) == len(outputs)

    for s, res in zip(inputs, outputs):
        (tmp_path / 'input.mod').write_text(s)
        monkeypatch.chdir(tmp_path)
        prolog_parser.main(['test', 'input.mod'])
        out, err = capsys.readouterr()
        assert err == ''
        assert out == res


def test_integrate_incorrect(tmp_path, monkeypatch, capsys):
    inputs = ['module test. module test2. a (b c) :- x, y, z.',
              'module test. type t f -> o. type t f -> o. f :- name. a (b c) :- x, y, z. type x y.',
              'type t f -> o. type t f -> o. f :- name. a (b c) :- x, y, z. module test.',
              'type t f -> o. type t f -> o f :- name. a (b c) :- x, y, z.',
              'module test. type t f -> o.. type t f -> o. f :- name. a (b c) :- x, y, z.',
              'module test. type t f -> o. type t f -> o f :- name. a (b c) :- x, y, z.',
              'module test. type t f -> o. (type t f -> o.)',
              'module test. (type t f -> o. type t f -> o.)']

    for s in inputs:
        (tmp_path / 'input.mod').write_text(s)
        monkeypatch.chdir(tmp_path)
        prolog_parser.main(['test', 'input.mod'])
        out, err = capsys.readouterr()
        assert re.match(r'Expected', out)


# test unit


def test_unit_ID():
    parser = PrologParser.ID.parse
    assert type(parser('qwerty')) == Success
    assert type(parser('asdlju7ayshdiKJHIDAKSJDI')) == Success
    assert type(parser('f')) == Success

    assert type(parser('qwerty.')) == Failure
    assert type(parser('Qwerty')) == Failure
    assert type(parser('type')) == Failure
    assert type(parser('module')) == Failure
    assert type(parser('.')) == Failure


def test_unit_VAR():
    parser = PrologParser.VAR.parse
    assert type(parser('Qwerty')) == Success
    assert type(parser('QSD9JIDJEIDIJJ')) == Success
    assert type(parser('F')) == Success

    assert type(parser('.')) == Failure
    assert type(parser('module')) == Failure
    assert type(parser('Qwerty.')) == Failure
    assert type(parser('qwerty')) == Failure
    assert type(parser('type')) == Failure


def test_unit_atom():
    parser = PrologParser.atom.parse
    assert type(parser('a B c D E f')) == Success
    assert type(parser('a (b C)')) == Success
    assert type(parser('a (b (c))')) == Success
    assert type(parser('a (b C) d E f')) == Success
    assert type(parser('a (b C) (((d ((E))))) f')) == Success
    assert type(parser('a (((c))) b')) == Success
    assert type(parser('a')) == Success
    assert type(parser('a ((A)) b')) == Success
    assert type(parser('a b c d')) == Success
    assert type(parser('a b C')) == Success

    assert type(parser('a ((b) c)')) == Failure
    assert type(parser('a (B c)')) == Failure
    assert type(parser('(a)')) == Failure
    assert type(parser('a b ()')) == Failure
    assert type(parser('A B c d')) == Failure
    assert type(parser('a (b c d')) == Failure
    assert type(parser('A b')) == Failure
    assert type(parser('a (((b (((c)) d e f))))')) == Failure
    assert type(parser('type b')) == Failure
    assert type(parser('(a) b c')) == Failure
    assert type(parser('a (((b c))')) == Failure
    assert type(parser('a module')) == Failure
    assert type(parser('A')) == Failure


def test_unit_module():
    parser = PrologParser.module.parse
    assert type(parser('module aSD9JIDJEIDIJJ.')) == Success
    assert type(parser('module f.')) == Success
    assert type(parser('module qwerty.')) == Success

    assert type(parser('module Qwerty.')) == Failure
    assert type(parser('module qwerty')) == Failure
    assert type(parser('module type.')) == Failure
    assert type(parser('module module.')) == Failure
    assert type(parser('module.')) == Failure
    assert type(parser('modUle qwerty.')) == Failure
    assert type(parser('module a b.')) == Failure
    assert type(parser('.')) == Failure


def test_unit_type():
    parser = PrologParser.typedef.parse
    assert type(parser('type fruit string -> string -> string -> o.')) == Success
    assert type(parser('type filter t.')) == Success
    assert type(parser('type filter ((A -> (B -> C -> (A -> list A) -> C))) -> o.')) == Success
    assert type(parser('type filter (A -> (B -> C -> (A -> list A) -> C)) -> o.')) == Success
    assert type(parser('type filter (A -> o) -> list A -> list A -> o.')) == Success
    assert type(parser('type filter (A -> (B -> C -> (A -> (list A)) -> C)) -> o.')) == Success
    assert type(parser('type filter string -> list A.')) == Success
    assert type(parser('type filter (A -> o) -> o.')) == Success

    assert type(parser('type foo ->.')) == Failure
    assert type(parser('tupe x o.')) == Failure
    assert type(parser('type type type -> type.')) == Failure
    assert type(parser('type x -> y -> z.')) == Failure
    assert type(parser('type.')) == Failure
    assert type(parser('type kavo.')) == Failure
    assert type(parser('.')) == Failure
    assert type(parser('type -> x.')) == Failure
    assert type(parser('type filter A -> B -> o')) == Failure


def test_unit_rel():
    parser = PrologParser.relation.parse
    assert type(parser('f a :- g, h (t c d).')) == Success
    assert type(parser('f :- g, (h; t).')) == Success
    assert type(parser('f :- (a ; (b)) , (((c ; d))).')) == Success
    assert type(parser('f.')) == Success
    assert type(parser('f :- g, h; t.')) == Success
    assert type(parser('f :- (((a))).')) == Success
    assert type(parser('f :- g.')) == Success
    assert type(parser('f (cons h t) :- g h, f t.')) == Success

    assert type(parser(':- f.')) == Failure
    assert type(parser('f :- .')) == Failure
    assert type(parser('f :- g; h, .')) == Failure
    assert type(parser('f (a.')) == Failure
    assert type(parser('(a) b.')) == Failure
    assert type(parser('f ().')) == Failure
    assert type(parser('(f).')) == Failure
    assert type(parser('f')) == Failure
    assert type(parser('f :- (g; (f).')) == Failure
