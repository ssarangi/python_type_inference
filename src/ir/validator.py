__author__ = 'sarangis'

from ir.exceptions import *
from ir.types import *
import inspect

# Code from http://typeandflow.blogspot.com/2011/06/python-decorator-with-optional-keyword.html
# Very well explained
def verify(func=None, **options):
    if func is not None:
        # We received the function on this call, so we can define
        # and return the inner function
        def inner(*args, **kwargs):
            if len(options) == 0:
                raise InvalidUsageModel("Expected verification arguments")

            original_func_args = inspect.getargspec(func).args

            for k, v in options.items():
                # Find the key in the original function
                idx = original_func_args.index(k)

                if (len(args) > idx):
                    # get the idx'th arg
                    arg = args[idx]
                else:
                    # Find in the keyword args
                    if k in kwargs:
                        arg = kwargs.get(k)

                if not isinstance(arg, v):
                    raise InvalidTypeException("Expected " + str(k) + " to be of type: " + v.__name__ + " but received type: " + str(type(k)))

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