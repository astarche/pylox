from pylox.lox import run


def _assert_std_out(capsys, expected):
    captured = capsys.readouterr()
    assert captured.out == expected


def _assert_out_lines(capsys, *expected_lines):
    expected = "\n".join(expected_lines) + "\n"
    _assert_std_out(capsys, expected)


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


def test_ifelse(capsys):
    run(
        """
        var x = 1;
        if (x) {
            print "TRUE";
        }

        if (x == 2) {
            print "Ack!";
        }
        else {
            print "Not 2";
        }

        var y = nil;
        if (y) {
            print "Ack null not true";
        }
        print "Done";
        """
    )

    _assert_out_lines(capsys, "TRUE", "Not 2", "Done")


def test_andor(capsys):
    run(
        """
        var x;
        print "Hello" or (x = 2);
        print x;
        print nil and (x = 3);
        print x;
        print false or (x = 4);
        print x;
        print "5" and (x = "Hello");
        print x;
        x = x and "World";
        print x;
        var y = true;
        x = y or nil;
        print x;
        y = false;
        print x and 1 or nil and y;
        """
    )
    _assert_out_lines(
        capsys, "Hello", "nil", "nil", "nil", "4", "4", "Hello", "Hello", "World", "true", "1"
    )


def test_while(capsys):
    run(
        """
        var x = 0;
        while (x < 10) {
            print x = x + 1;
        }
        """
    )

    _assert_out_lines(capsys, *[str(i + 1) for i in range(0, 10)])


def test_while_zeroiteration(capsys):
    run(
        """
        var x = 100;
        while (x = nil) print "Why?";
        print x;
        """
    )

    _assert_out_lines(capsys, "nil")


def test_for(capsys):
    run(
        """
        for (var x = 0; x < 10; x = x + 1) {
            print x;
        }
        """
    )
    _assert_out_lines(capsys, *[str(i) for i in range(0, 10)])


def test_for_deconstructed(capsys):
    run(
        """
        var x = 0;
        for (; x < 10;) {
            print x;
            x = x + 1;
        }
        """
    )
    _assert_out_lines(capsys, *[str(i) for i in range(0, 10)])


def test_for_empty(capsys):
    run(
        """
        var x = 0;
        for (;;) {
            print x;
            // Bail out of infinite loop with bad var access.
            print y;
        }
        """
    )
    _assert_out_lines(capsys, "0", "Error (6): Attempt to access undefined variable y")


def test_clock(capsys):
    run(
        """
        var t = clock();
        print t > 1.0;
        print clock() >= t;
        """
    )

    _assert_out_lines(capsys, "true", "true")
