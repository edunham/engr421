def foo(a):
    # assume a bunch of time is wasted here for reasons
    if a == 4:
        return False
    else:
        return a + 1

def main():
    b = int(raw_input("an int: "))
    # it's concise to call twice, like so:
    if foo(b):
        c = foo(b)
    # and ugly but fast to call just once:
    temp = foo(b)
    if temp:
        c = temp
    # is there a concise way to write that with only one call?

if __name__ == "__main__":
    main()      
