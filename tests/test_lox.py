from pylox.lox import run


def _assert_std_out(capsys, expected):
    captured = capsys.readouterr()
    assert captured.out == expected


def test_helloworld(capsys):
    run('print "Hello World";')

    _assert_std_out(capsys, "Hello World\n")


def test_add(capsys):
    run("print 1 + 2 + 100;")

    _assert_std_out(capsys, "103\n")


def test_addfloat(capsys):
    run("print 1 + 0.25;")

    _assert_std_out(capsys, "1.25\n")


def test_expr(capsys):
    run("print 100 * 10 * (5 + 2);")

    _assert_std_out(capsys, "7000\n")


def test_multiline(capsys):
    run(
        """
    print 1;
    print "cool string";
    print 100 * 8 / (7 + 1);
    """
    )

    _assert_std_out(capsys, "1\ncool string\n100\n")


def test_define_access_update(capsys):
    run(
        """
        var x = 1;
        print x;
        x = 2;
        print x + 1;
        """
    )

    _assert_std_out(capsys, "1\n3\n")


def test_block(capsys):
    run(
        """
        var x = 1;
        {
            var x = 5;
            print x;
            {
                var x = x + 10;
                print x;
            }
            print x;
        }
        print x;
        """
    )

    _assert_std_out(capsys, "5\n15\n5\n1\n")
