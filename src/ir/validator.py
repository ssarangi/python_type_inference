__author__ = 'sarangis'

# Code from http://typeandflow.blogspot.com/2011/06/python-decorator-with-optional-keyword.html
# Very well explained
class U:
    def __init__(self, *args):
        self.types = args

    def __str__(self):
        return ",".join(self.types)

    __repr__ = __str__

def verify(func=None, **options):
    if func is not None:
        # We received the function on this call, so we can define
        # and return the inner function
        def inner(*args, **kwargs):
            if len(options) == 0:
                raise Exception("Expected verification arguments")

            func_code = func.__code__
            arg_names = func_code.co_varnames

            for k, v in options.items():
                # Find the key in the original function
                idx = arg_names.index(k)

                if (len(args) > idx):
                    # get the idx'th arg
                    arg = args[idx]
                else:
                    # Find in the keyword args
                    if k in kwargs:
                        arg = kwargs.get(k)

                if isinstance(v, U):
                    # Unroll the types to check for multiple types
                    types_match = False
                    for dtype in v.types:
                        if isinstance(arg, dtype):
                            types_match = True

                    if types_match == False:
                        raise Exception("Expected " + str(k) + " to be of type: " + str(v) + " but received type: " + str(type(arg)))
                elif not isinstance(arg, v):
                    raise Exception("Expected " + str(k) + " to be of type: " + v.__name__ + " but received type: " + str(type(arg)))

            output = func(*args, **kwargs)
            return output

        return inner
    else:
        # We didn't receive the function on this call, so the return value
        # of this call will receive it, and we're getting the options now.
        def partial_inner(func):
            return verify(func, **options)
        return partial_inner


class Validator:
    def validate(self):
        raise NotImplementedError("Validation method has to be implemented")