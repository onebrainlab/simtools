# -*- coding: utf-8 -*-
"""Unit tests of parameter services."""

import csv
import json
import math
import os

import pytest

from simtools.exceptions import ParamFileError
from simtools.params import ParamSets, Params


@pytest.fixture
def params():
    p = Params()
    p.p1 = 1
    p.p2 = 2.5
    p.p3 = math.pi
    p.p4 = "abc"
    p.p5 = None
    p.p6 = {'a': 1, 'b': 2.5, 'c': math.pi, 'd': "abc", 'e': None}
    p.p7 = 1, 2.5, math.pi, "abc", None
    p.p8 = [1, 2.5, math.pi, "abc", None]
    return p


def test_params_load_json(tmpdir):
    # Correct
    params_file = tmpdir.join("params_ok.json")
    params_file.write(
"""{
    "p1": 1,
    "p2": 2.5,
    "p3": 3.141592653589793,
    "p4": "abc",
    "p5": null,
    "p6": {
        "a": 1,
        "b": 2.5,
        "c": 3.141592653589793,
        "d": "abc",
        "e": null
    },
    "p7": [
        1,
        2.5,
        3.141592653589793,
        "abc",
        null
    ]
}""")
    p = Params()

    p.load(str(params_file))
    assert p.p1 == 1
    assert p.p2 == 2.5
    assert p.p3 == math.pi
    assert p.p4 == "abc"
    assert p.p5 == None
    assert p.p6 == {'a': 1, 'b': 2.5, 'c': math.pi, 'd': "abc", 'e': None}
    assert p.p7 == [1, 2.5, math.pi, "abc", None]

    # Syntax error
    params_file = tmpdir.join("params_syntax.json")
    params_file.write(
"""\"p1": 1,
"p2": 2.5,
"p3": 3.141592653589793,
"p4": "abc",
"p5": null,
"p6": {
    "a": 1,
    "b": 2.5,
    "c": 3.141592653589793,
    "d": "abc",
    "e": null
},
"p7": [
    1,
    2.5,
    3.141592653589793,
    "abc",
    null
]""")
    p = Params()

    with pytest.raises(ParamFileError):
        p.load(str(params_file))


def test_params_load_py(tmpdir):
    # Correct
    params_file = tmpdir.join("params_ok.py")
    params_file.write(
"""import math

p1 = 1
p2 = 2.5
p3 = math.pi
p4 = "abc"
p5 = None
p6 = {'a': 1, 'b': 2.5, 'c': math.pi, 'd': "abc", 'e': None}
p7 = 1, 2.5, math.pi, "abc", None
p8 = [1, 2.5, math.pi, "abc", None]
p9 = [x+x for x in [1, 2, 3]]  # list comprehension
""")
    p = Params()

    p.load(str(params_file))
    assert p.p1 == 1
    assert p.p2 == 2.5
    assert p.p3 == math.pi
    assert p.p4 == "abc"
    assert p.p5 == None
    assert p.p6 == {'a': 1, 'b': 2.5, 'c': math.pi, 'd': "abc", 'e': None}
    assert p.p7 == (1, 2.5, math.pi, "abc", None)
    assert p.p8 == [1, 2.5, math.pi, "abc", None]
    assert p.p9 == [2, 4, 6]
    with pytest.raises(AttributeError):
        p.math

    # Syntax error
    params_file = tmpdir.join("params_syntax.py")
    params_file.write(
"""p1 = 5
p2 = [x+x for x in]
""")
    p = Params()

    with pytest.raises(ParamFileError):
        p.load(str(params_file))

    # Division by 0
    params_file = tmpdir.join("params_div_zero.py")
    params_file.write(
"""p1 = 5
p2 = 5 / 0
""")
    p = Params()

    with pytest.raises(ParamFileError):
        p.load(str(params_file))

    # Undefined name
    params_file = tmpdir.join("params_undef_name.py")
    params_file.write(
"""p1 = 5
p2
""")
    p = Params()

    with pytest.raises(ParamFileError):
        p.load(str(params_file))


def test_params_load_no_ext(tmpdir):
    params_file = tmpdir.join("params_no_ext")
    p = Params()

    with pytest.raises(ValueError):
        p.load(str(params_file))


def test_params_save_default(tmpdir, params):
    params_file = tmpdir.join("params_default.json")

    params.save(str(params_file))
    params_json = json.load(params_file)
    for p in ('p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p8'):
        assert params_json[p] == params[p]
    assert params_json['p7'] == list(params['p7'])


def test_params_save_paramnames(tmpdir, params):
    # All parameters
    params_file = tmpdir.join("params_all.json")
    paramnames = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8']

    params.save(str(params_file), paramnames)
    params_json = json.load(params_file)
    for p in ('p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p8'):
        assert params_json[p] == params[p]
    assert params_json['p7'] == list(params['p7'])

    # Some parameters
    params_file = tmpdir.join("params_some.json")
    paramnames = ['p1', 'p4', 'p8']

    params.save(str(params_file), paramnames)
    params_json = json.load(params_file)
    for p in ('p1', 'p4', 'p8'):
        assert params_json[p] == params[p]
    for p in ('p2', 'p3', 'p5', 'p6', 'p7'):
        with pytest.raises(KeyError):
            assert params_json[p] == params[p]

    # Not iterable
    params_file = tmpdir.join("params_notiter.json")
    paramnames = 1

    with pytest.raises(TypeError):
        params.save(str(params_file), paramnames)

    # String
    params_file = tmpdir.join("params_string.json")
    paramnames = "p1, p2, p3, p4, p5, p6, p7, p8"

    with pytest.raises(TypeError):
        params.save(str(params_file), paramnames)

    # Non-existing parameter
    params_file = tmpdir.join("params_nonexist.json")
    paramnames = ['p1', 'p999']

    with pytest.raises(ValueError):
        params.save(str(params_file), paramnames)

    # Repeated parameter
    params_file = tmpdir.join("params_repeated.json")
    paramnames = ['p1', 'p2', 'p3', 'p2', 'p4', 'p5', 'p6', 'p7', 'p8']

    with pytest.raises(ValueError):
        params.save(str(params_file), paramnames)


def test_params_save_indent(tmpdir, params):
    # Indent = 4
    params_file = tmpdir.join("params_indent4.json")

    params.save(str(params_file), indent=4)
    n_bytes4 = params_file.size()
    n_lines4 = len(params_file.readlines())
    assert n_lines4 == 28

    # Indent = 2
    params_file = tmpdir.join("params_indent2.json")

    params.save(str(params_file), indent=2)
    n_bytes2 = params_file.size()
    assert n_bytes2 < n_bytes4
    n_lines2 = len(params_file.readlines())
    assert n_lines2 == 28

    # Indent = None
    params_file = tmpdir.join("params_indentnone.json")

    params.save(str(params_file), indent=None)
    n_bytes_none = params_file.size()
    assert n_bytes_none < n_bytes2
    n_lines_none = len(params_file.readlines())
    assert n_lines_none == 1


@pytest.mark.parametrize('kwargs', [
    {'fp': None},
    {'obj': None}])
def test_params_save_forbid_kwargs(tmpdir, params, kwargs):
    params_file = tmpdir.join("params_forbidkw.json")

    with pytest.raises(TypeError):
        params.save(str(params_file), **kwargs)


def test_paramsets_mutable_sequence():
    # Empty
    paramsets = ParamSets()
    assert len(paramsets) == 0
    with pytest.raises(IndexError):
        paramsets[0]
    with pytest.raises(StopIteration):
        iter(paramsets).next()
    with pytest.raises(StopIteration):
        reversed(paramsets).next()

    # Append
    p0 = Params({'p1': 1, 'p2': 2.5, 'p3': "abc", 'p4': None})
    p1 = Params({'p1': 10, 'p2': 20.5, 'p3': "def", 'p4': None})

    paramsets.append(p0)
    assert len(paramsets) == 1
    assert p0 in paramsets
    assert paramsets[0] == p0
    assert p1 not in paramsets

    paramsets.append(p1)
    assert len(paramsets) == 2
    assert p1 in paramsets
    assert paramsets[1] == p1

    # Insert
    paramsets.insert(0, p1)
    assert len(paramsets) == 3
    assert paramsets[0] == p1
    assert paramsets[1] == p0
    assert paramsets[2] == p1

    with pytest.raises(TypeError):
        paramsets.insert(0, "p1 = 1")

    # Set
    paramsets[0] = p0
    assert len(paramsets) == 3
    assert paramsets[0] == p0
    assert paramsets[1] == p0
    assert paramsets[2] == p1

    with pytest.raises(IndexError):
        paramsets[3] = p0

    with pytest.raises(TypeError):
        paramsets[0] = "p1 = 1"

    # Delete
    del paramsets[1]
    assert len(paramsets) == 2
    assert paramsets[0] == p0
    assert paramsets[1] == p1

    with pytest.raises(IndexError):
        del paramsets[2]

    # Iterator
    paramsets_list = [p0, p1]

    for paramset, paramset_l in zip(paramsets, paramsets_list):
        assert paramset == paramset_l

    # Reverse iterator
    paramsets_list = [p1, p0]

    for paramset, paramset_l in zip(reversed(paramsets), paramsets_list):
        assert paramset == paramset_l


def test_paramsets_load_params(tmpdir):
    params_file_json = tmpdir.join("params.json")
    params_file_json.write(
"""{
    "p1": 1,
    "p2": 2.5,
    "p3": "abc",
    "p4": null
}""")
    params_file_py = tmpdir.join("params.py")
    params_file_py.write(
"""p1 = 1
p2 = 2.5
p3 = "abc"
p4 = None
""")
    paramsets = ParamSets()

    # First parameter set (from a JSON file)
    paramsets.load_params(str(params_file_json))
    assert len(paramsets) == 1
    assert paramsets[0].p1 == 1
    assert paramsets[0].p2 == 2.5
    assert paramsets[0].p3 == "abc"
    assert paramsets[0].p4 == None
    with pytest.raises(IndexError):
        paramsets[1]

    # Second parameter set (from a Python file)
    paramsets.load_params(str(params_file_py))
    assert len(paramsets) == 2
    assert paramsets[1].p1 == 1
    assert paramsets[1].p2 == 2.5
    assert paramsets[1].p3 == "abc"
    assert paramsets[0].p4 == None
    with pytest.raises(IndexError):
        paramsets[2]


def test_paramsets_save_csv(tmpdir):
    # Default (with header and without record numbers)
    paramsets_file = tmpdir.join("paramsets_default.csv")
    p0 = Params({'p1': 1, 'p2': 2.5, 'p3': "abc", 'p4': "", 'p5': None})
    p1 = Params({'p1': None, 'p2': 20.5, 'p3': "", 'p4': "def", 'p5': 10})
    paramsets = ParamSets()
    paramsets.append(p0)
    paramsets.append(p1)

    paramsets.save(str(paramsets_file), ['p1', 'p2', 'p3', 'p4', 'p5'])
    assert paramsets[0] == p0
    assert paramsets[1] == p1
    with paramsets_file.open() as paramsets_file:
        csv_reader = csv.DictReader(paramsets_file, dialect='excel-tab')
        for csv_row, paramset in zip(csv_reader, paramsets):
            for p in ('p1', 'p2', 'p3', 'p4', 'p5'):
                assert csv_row[p] == str(paramset[p])

    # With header and with record numbers
    paramsets_file = tmpdir.join("paramsets_head_num.csv")

    paramsets.save(str(paramsets_file), ['p1', 'p2', 'p3', 'p4', 'p5'],
                   with_numbers=True, with_header=True)
    assert paramsets[0] == p0
    assert paramsets[1] == p1
    with paramsets_file.open() as paramsets_file:
        csv_reader = csv.DictReader(paramsets_file, dialect='excel-tab')
        for r, (csv_row, paramset) in enumerate(zip(csv_reader, paramsets),
                                                start=1):
            assert csv_row['#'] == str(r)
            for p in ('p1', 'p2', 'p3', 'p4', 'p5'):
                assert csv_row[p] == str(paramset[p])

    # Without header and without record numbers
    paramsets_file = tmpdir.join("paramsets.csv")

    paramsets.save(str(paramsets_file), ['p1', 'p2', 'p3', 'p4', 'p5'],
                   with_numbers=False, with_header=False)
    assert paramsets[0] == p0
    assert paramsets[1] == p1
    with paramsets_file.open() as paramsets_file:
        csv_reader = csv.DictReader(paramsets_file,
                                    ['p1', 'p2', 'p3', 'p4', 'p5'],
                                    dialect='excel-tab')
        for csv_row, paramset in zip(csv_reader, paramsets):
            for p in ('p1', 'p2', 'p3', 'p4', 'p5'):
                assert csv_row[p] == str(paramset[p])

    # Without header and with record numbers
    paramsets_file = tmpdir.join("paramsets_num.csv")

    paramsets.save(str(paramsets_file), ['p1', 'p2', 'p3', 'p4', 'p5'],
                   with_numbers=True, with_header=False)
    assert paramsets[0] == p0
    assert paramsets[1] == p1
    with paramsets_file.open() as paramsets_file:
        csv_reader = csv.DictReader(paramsets_file,
                                    ['#', 'p1', 'p2', 'p3', 'p4', 'p5'],
                                    dialect='excel-tab')
        for r, (csv_row, paramset) in enumerate(zip(csv_reader, paramsets),
                                                start=1):
            assert csv_row['#'] == str(r)
            for p in ('p1', 'p2', 'p3', 'p4', 'p5'):
                assert csv_row[p] == str(paramset[p])


def test_paramsets_save_csv_paramnames(tmpdir):
    # All parameters passed as a tuple, with record numbers
    paramsets_file = tmpdir.join("paramsets_tuple_num.csv")
    p0 = Params({'p1': 1, 'p2': 2.5, 'p3': "abc", 'p4': None})
    p1 = Params({'p1': 10, 'p2': 20.5, 'p3': "def", 'p4': None})
    paramsets = ParamSets()
    paramsets.append(p0)
    paramsets.append(p1)
    paramnames = 'p1', 'p2', 'p3', 'p4'

    paramsets.save(str(paramsets_file), paramnames, with_numbers=True)
    with paramsets_file.open() as paramsets_file:
        csv_reader = csv.DictReader(paramsets_file, dialect='excel-tab')
        for r, (csv_row, paramset) in enumerate(zip(csv_reader, paramsets),
                                                start=1):
            assert csv_row['#'] == str(r)
            for p in ('p1', 'p2', 'p3', 'p4'):
                assert csv_row[p] == str(paramset[p])

    # Some parameters passed as a tuple
    paramsets_file = tmpdir.join("paramsets_some.csv")
    paramnames = 'p1', 'p4'

    paramsets.save(str(paramsets_file), paramnames)
    with paramsets_file.open() as paramsets_file:
        csv_reader = csv.DictReader(paramsets_file, dialect='excel-tab')
        for csv_row, paramset in zip(csv_reader, paramsets):
            for p in ('p1', 'p4'):
                assert csv_row[p] == str(paramset[p])
            for p in ('p2', 'p3'):
                with pytest.raises(KeyError):
                    assert csv_row[p] == str(paramset[p])

    # Not iterable
    paramsets_file = tmpdir.join("paramsets_notiter.csv")
    paramnames = 1

    with pytest.raises(TypeError):
        paramsets.save(str(paramsets_file), paramnames)

    # String
    paramsets_file = tmpdir.join("paramsets_string.csv")
    paramnames = "p1, p2, p3, p4"

    with pytest.raises(TypeError):
        paramsets.save(str(paramsets_file), paramnames)

    # Non-existing parameter
    paramsets_file = tmpdir.join("paramsets_nonexist.csv")
    paramnames = ['p1', 'p999']

    with pytest.raises(ValueError):
        paramsets.save(str(paramsets_file), paramnames)
    assert not os.path.isfile(str(paramsets_file))

    # Repeated parameter
    paramsets_file = tmpdir.join("paramsets_repeated.csv")
    paramnames = ['p1', 'p2', 'p3', 'p2', 'p4']

    with pytest.raises(ValueError):
        paramsets.save(str(paramsets_file), paramnames)


def test_paramsets_save_csv_nested(tmpdir):
    # Correct
    paramsets_file = tmpdir.join("paramsets_ok.csv")
    p0 = Params({'p1': {'a': 1, 'b': 2.5}, 'p2': ["abc", "def"]})
    p1 = Params({'p1': {'a': 10, 'b': 20.5}, 'p2': ["uvw", "xyz"]})
    paramsets = ParamSets()
    paramsets.append(p0)
    paramsets.append(p1)

    paramsets.save(str(paramsets_file),
                   ["p1['a']", "p1['b']", 'p2[0]', 'p2[1]'])
    with paramsets_file.open() as paramsets_file:
        csv_reader = csv.DictReader(paramsets_file, dialect='excel-tab')
        for csv_row, paramset in zip(csv_reader, paramsets):
            paramnames_csv = sorted(csv_row.keys())  # needed to avoid
                                                     # confusion between single
                                                     # and double quotes
            assert csv_row[paramnames_csv[0]] == str(paramset['p1']['a'])
            assert csv_row[paramnames_csv[1]] == str(paramset['p1']['b'])
            assert csv_row['p2[0]'] == str(paramset['p2'][0])
            assert csv_row['p2[1]'] == str(paramset['p2'][1])

    # Syntax error
    paramsets_file = tmpdir.join("paramsets_syntax.csv")

    with pytest.raises(ValueError):
        paramsets.save(str(paramsets_file), ["p1['a']", "p1["])
    assert not os.path.isfile(str(paramsets_file))

    # Illegal key
    paramsets_file = tmpdir.join("paramsets_key.csv")

    with pytest.raises(ValueError):
        paramsets.save(str(paramsets_file), ["p1['a']", "p1['z']"])
    assert not os.path.isfile(str(paramsets_file))

    # Illegal index
    paramsets_file = tmpdir.join("paramsets_index.csv")

    with pytest.raises(ValueError):
        paramsets.save(str(paramsets_file), ['p2[0]', 'p2[9]'])
    assert not os.path.isfile(str(paramsets_file))


def test_paramsets_save_csv_map(tmpdir):
    # Correct
    paramsets_file = tmpdir.join("paramsets_ok.csv")
    p0 = Params({'p1': {'a': 1, 'b': 2.5}, 'p2': ["abc", "def"]})
    p1 = Params({'p1': {'a': 10, 'b': 20.5}, 'p2': ["uvw", "xyz"]})
    paramsets = ParamSets()
    paramsets.append(p0)
    paramsets.append(p1)
    paramnames = ["p1['a']", "p1['b']", 'p2[0]', 'p2[1]']
    paramnames_map = {"p1['a']": 'p1a', 'p2[0]': 'p20'}

    paramsets.save(str(paramsets_file), paramnames, paramnames_map)
    with paramsets_file.open() as paramsets_file:
        csv_reader = csv.DictReader(paramsets_file, dialect='excel-tab')
        for csv_row, paramset in zip(csv_reader, paramsets):
            paramnames_csv = sorted(csv_row.keys())  # needed to avoid
                                                     # confusion between single
                                                     # and double quotes
            assert csv_row['p1a'] == str(paramset['p1']['a'])
            assert csv_row[paramnames_csv[0]] == str(paramset['p1']['b'])
            assert csv_row['p20'] == str(paramset['p2'][0])
            assert csv_row['p2[1]'] == str(paramset['p2'][1])
            assert 'p2[0]' not in csv_row

    # Non-existing parameter
    paramsets_file = tmpdir.join("paramsets_nonexist.csv")
    paramnames_map = {"p1['a']": 'p1a', 'p999[0]': 'p9990'}

    with pytest.raises(ValueError):
        paramsets.save(str(paramsets_file), paramnames, paramnames_map)

    # Repeated parameter
    paramsets_file = tmpdir.join("paramsets_repeated.csv")
    paramnames_map = {"p1['a']": 'p1a', 'p2[0]': 'p1a'}

    with pytest.raises(ValueError):
        paramsets.save(str(paramsets_file), paramnames, paramnames_map)

    # Non-unique parameter
    paramsets_file = tmpdir.join("paramsets_nonunique.csv")
    paramnames_map = {"p1['a']": 'p1a', 'p2[0]': 'p2[1]'}

    with pytest.raises(ValueError):
        paramsets.save(str(paramsets_file), paramnames, paramnames_map)


def test_paramsets_save_csv_invalid_kwargs(tmpdir):
    paramsets_file = tmpdir.join("paramsets_invalidkw.csv")
    p0 = Params({'p1': 1, 'p2': 2.5, 'p3': "abc"})
    p1 = Params({'p1': 10, 'p2': 20.5, 'p3': "def"})
    paramsets = ParamSets()
    paramsets.append(p0)
    paramsets.append(p1)

    with pytest.raises(TypeError):
        paramsets.save(str(paramsets_file), ['p1', 'p2', 'p3'], indent=2)


def test_paramsets_save_json(tmpdir):
    # Default (without record numbers)
    paramsets_file = tmpdir.join("paramsets_default.json")
    p0 = Params({'p1': 1, 'p2': 2.5, 'p3': "abc", 'p4': "", 'p5': None})
    p1 = Params({'p1': None, 'p2': 20.5, 'p3': "", 'p4': "def", 'p5': 10})
    paramsets = ParamSets()
    paramsets.append(p0)
    paramsets.append(p1)

    paramsets.save(str(paramsets_file), ['p1', 'p2', 'p3', 'p4', 'p5'])
    assert paramsets[0] == p0
    assert paramsets[1] == p1
    paramsets_json = json.load(paramsets_file)
    for paramset_json, paramset in zip(paramsets_json, paramsets):
        for p in ('p1', 'p2', 'p3', 'p4', 'p5'):
            assert paramset_json[p] == paramset[p]

    # With record numbers
    paramsets_file = tmpdir.join("paramsets_num.json")

    paramsets.save(str(paramsets_file), ['p1', 'p2', 'p3', 'p4', 'p5'],
                   with_numbers=True)
    assert paramsets[0] == p0
    assert paramsets[1] == p1
    paramsets_json = json.load(paramsets_file)
    for r, (paramset_json, paramset) in enumerate(zip(paramsets_json,
                                                      paramsets),
                                                  start=1):
        assert paramset_json['#'] == r
        for p in ('p1', 'p2', 'p3', 'p4', 'p5'):
            assert paramset_json[p] == paramset[p]


def test_paramsets_save_json_paramnames(tmpdir):
    # All parameters passed as a tuple, with record numbers
    paramsets_file = tmpdir.join("paramsets_tuple_num.json")
    p0 = Params({'p1': 1, 'p2': 2.5, 'p3': "abc", 'p4': None})
    p1 = Params({'p1': 10, 'p2': 20.5, 'p3': "def", 'p4': None})
    paramsets = ParamSets()
    paramsets.append(p0)
    paramsets.append(p1)
    paramnames = 'p1', 'p2', 'p3', 'p4'

    paramsets.save(str(paramsets_file), paramnames, with_numbers=True)
    paramsets_json = json.load(paramsets_file)
    for r, (paramset_json, paramset) in enumerate(zip(paramsets_json,
                                                      paramsets),
                                                  start=1):
        assert paramset_json['#'] == r
        for p in ('p1', 'p2', 'p3', 'p4'):
            assert paramset_json[p] == paramset[p]

    # Some parameters passed as a tuple
    paramsets_file = tmpdir.join("paramsets_some.json")
    paramnames = 'p1', 'p4'

    paramsets.save(str(paramsets_file), paramnames)
    paramsets_json = json.load(paramsets_file)
    for paramset_json, paramset in zip(paramsets_json, paramsets):
        for p in ('p1', 'p4'):
            assert paramset_json[p] == paramset[p]
        for p in ('p2', 'p3'):
            with pytest.raises(KeyError):
                assert paramset_json[p] == paramset[p]

    # Not iterable
    paramsets_file = tmpdir.join("paramsets_notiter.json")
    paramnames = 1

    with pytest.raises(TypeError):
        paramsets.save(str(paramsets_file), paramnames)

    # String
    paramsets_file = tmpdir.join("paramsets_string.json")
    paramnames = "p1, p2, p3, p4"

    with pytest.raises(TypeError):
        paramsets.save(str(paramsets_file), paramnames)

    # Non-existing parameter
    paramsets_file = tmpdir.join("paramsets_nonexist.json")
    paramnames = ['p1', 'p999']

    with pytest.raises(ValueError):
        paramsets.save(str(paramsets_file), paramnames)
    assert not os.path.isfile(str(paramsets_file))

    # Repeated parameter
    paramsets_file = tmpdir.join("paramsets_repeated.json")
    paramnames = ['p1', 'p2', 'p3', 'p2', 'p4']

    with pytest.raises(ValueError):
        paramsets.save(str(paramsets_file), paramnames)


def test_paramsets_save_json_nested(tmpdir):
    # Correct
    paramsets_file = tmpdir.join("paramsets_ok.json")
    p0 = Params({'p1': {'a': 1, 'b': 2.5}, 'p2': ["abc", "def"]})
    p1 = Params({'p1': {'a': 10, 'b': 20.5}, 'p2': ["uvw", "xyz"]})
    paramsets = ParamSets()
    paramsets.append(p0)
    paramsets.append(p1)

    paramsets.save(str(paramsets_file),
                   ["p1['a']", "p1['b']", 'p2[0]', 'p2[1]'])
    paramsets_json = json.load(paramsets_file)
    for paramset_json, paramset in zip(paramsets_json, paramsets):
        paramnames_json = sorted(paramset_json.keys())  # needed to avoid
                                                        # confusion between
                                                        # single and double
                                                        # quotes
        assert paramset_json[paramnames_json[0]] == paramset['p1']['a']
        assert paramset_json[paramnames_json[1]] == paramset['p1']['b']
        assert paramset_json['p2[0]'] == paramset['p2'][0]
        assert paramset_json['p2[1]'] == paramset['p2'][1]

    # Syntax error
    paramsets_file = tmpdir.join("paramsets_syntax.json")

    with pytest.raises(ValueError):
        paramsets.save(str(paramsets_file), ["p1['a']", "p1["])
    assert not os.path.isfile(str(paramsets_file))

    # Illegal key
    paramsets_file = tmpdir.join("paramsets_key.json")

    with pytest.raises(ValueError):
        paramsets.save(str(paramsets_file), ["p1['a']", "p1['z']"])
    assert not os.path.isfile(str(paramsets_file))

    # Illegal index
    paramsets_file = tmpdir.join("paramsets_index.json")

    with pytest.raises(ValueError):
        paramsets.save(str(paramsets_file), ['p2[0]', 'p2[9]'])
    assert not os.path.isfile(str(paramsets_file))


def test_paramsets_save_json_map(tmpdir):
    # Correct
    paramsets_file = tmpdir.join("paramsets_ok.json")
    p0 = Params({'p1': {'a': 1, 'b': 2.5}, 'p2': ["abc", "def"]})
    p1 = Params({'p1': {'a': 10, 'b': 20.5}, 'p2': ["uvw", "xyz"]})
    paramsets = ParamSets()
    paramsets.append(p0)
    paramsets.append(p1)
    paramnames = ["p1['a']", "p1['b']", 'p2[0]', 'p2[1]']
    paramnames_map = {"p1['a']": 'p1a', 'p2[0]': 'p20'}

    paramsets.save(str(paramsets_file), paramnames, paramnames_map)
    paramsets_json = json.load(paramsets_file)
    for paramset_json, paramset in zip(paramsets_json, paramsets):
        paramnames_json = sorted(paramset_json.keys())  # needed to avoid
                                                        # confusion between
                                                        # single and double
                                                        # quotes
        assert paramset_json['p1a'] == paramset['p1']['a']
        assert paramset_json[paramnames_json[0]] == paramset['p1']['b']
        assert paramset_json['p20'] == paramset['p2'][0]
        assert paramset_json['p2[1]'] == paramset['p2'][1]
        assert 'p2[0]' not in paramset_json

    # Non-existing parameter
    paramsets_file = tmpdir.join("paramsets_nonexist.json")
    paramnames_map = {"p1['a']": 'p1a', 'p999[0]': 'p9990'}

    with pytest.raises(ValueError):
        paramsets.save(str(paramsets_file), paramnames, paramnames_map)

    # Repeated parameter
    paramsets_file = tmpdir.join("paramsets_repeated.json")
    paramnames_map = {"p1['a']": 'p1a', 'p2[0]': 'p1a'}

    with pytest.raises(ValueError):
        paramsets.save(str(paramsets_file), paramnames, paramnames_map)

    # Non-unique parameter
    paramsets_file = tmpdir.join("paramsets_nonunique.json")
    paramnames_map = {"p1['a']": 'p1a', 'p2[0]': 'p2[1]'}

    with pytest.raises(ValueError):
        paramsets.save(str(paramsets_file), paramnames, paramnames_map)


def test_paramsets_save_json_indent(tmpdir):
    # Indent = 4
    paramsets_file = tmpdir.join("paramsets_indent4.json")
    p0 = Params({'p1': 1, 'p2': 2.5, 'p3': "abc"})
    p1 = Params({'p1': 10, 'p2': 20.5, 'p3': "def"})
    paramsets = ParamSets()
    paramsets.append(p0)
    paramsets.append(p1)

    paramsets.save(str(paramsets_file), ['p1', 'p2', 'p3'], indent=4)
    n_bytes4 = paramsets_file.size()
    n_lines4 = len(paramsets_file.readlines())
    assert n_lines4 == 12

    # Indent = 2
    paramsets_file = tmpdir.join("paramsets_indent2.json")

    paramsets.save(str(paramsets_file), ['p1', 'p2', 'p3'], indent=2)
    n_bytes2 = paramsets_file.size()
    assert n_bytes2 < n_bytes4
    n_lines2 = len(paramsets_file.readlines())
    assert n_lines2 == 12

    # Indent = None
    paramsets_file = tmpdir.join("paramsets_indentnone.json")

    paramsets.save(str(paramsets_file), ['p1', 'p2', 'p3'], indent=None)
    n_bytes_none = paramsets_file.size()
    assert n_bytes_none < n_bytes2
    n_lines_none = len(paramsets_file.readlines())
    assert n_lines_none == 1


@pytest.mark.parametrize('kwargs', [
    {'fp': None},
    {'obj': None},
    {'with_header': False}])
def test_paramsets_save_json_invalid_kwargs(tmpdir, kwargs):
    paramsets_file = tmpdir.join("paramsets_invalidkw.json")
    p0 = Params({'p1': 1, 'p2': 2.5, 'p3': "abc"})
    p1 = Params({'p1': 10, 'p2': 20.5, 'p3': "def"})
    paramsets = ParamSets()
    paramsets.append(p0)
    paramsets.append(p1)

    with pytest.raises(TypeError):
        paramsets.save(str(paramsets_file), ['p1', 'p2', 'p3'], **kwargs)
