print 'start'
RA_iter = xrange(1, 101).__iter__()
while True:
    try:
        i = RA_iter.next()

        if 1 != 1:
            print "firstif"
            raise ArithmeticError("arithexpt")
        else:
            if 1 == 1:
                print "nestedif"
                raise StopIteration("iterexpt")

        print "end of tryexcept"

    except StopIteration:
        print "in stopiteration handler"
        break
    except ArithmeticError:
        print "in arithmetic error exception handler"
    print 'whilebody1'
    print 'whilebody12'
print 'end'