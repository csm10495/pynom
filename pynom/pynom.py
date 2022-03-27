import collections
import dataclasses
import datetime
import traceback
import types
import typing


@dataclasses.dataclass
class ExceptionInfo:
    """A dataclass containing an exception, traceback, and approximate timestamp"""

    exception: Exception
    traceback: types.TracebackType
    time_stamp: datetime.datetime

    def __str__(self):
        ret_str = f"{type(self.exception).__name__}: thrown at {self.time_stamp}\n"
        ret_str += "  " + str(self.exception).replace("\n", "\n  ").rstrip(" ")
        ret_str += "    " + ("\n".join(traceback.format_tb(self.traceback))).replace(
            "\n", "\n   "
        ).rstrip(" ")
        return ret_str


class CombinedException(Exception):
    """An exception that will be raised containing the currently eatten exceptions of the same type"""

    def __init__(self, exception_infos: typing.List[ExceptionInfo]):
        self.exception_infos = exception_infos

    def __str__(self):
        return "CombinedException:\n  " + (
            "\n".join([str(a) for a in self.exception_infos])
        ).replace("\n", "\n  ").rstrip(" ")


class PyNom:
    #: A special variable that corresponds with an exception type leading to all exceptions being eatten even if not listed in exception_types_to_eat
    ALL_EXCEPTIONS = "ALL_EXCEPTIONS"

    def __init__(
        self,
        exception_types_to_eat: list,
        max_to_eat_before_throw_up: int,
        throw_up_action: typing.Union[typing.Callable, None] = None,
        side_dish_action: typing.Union[typing.Callable, None] = None,
        digest_time: typing.Union[datetime.timedelta, None] = None,
        digest_action: typing.Union[typing.Callable, None] = None,
    ):
        """Instantiate a PyNom object

        Args:
            exception_types_to_eat: A list of exception types that PyNom should eat.
                Note that if PyNom.ALL_EXCEPTIONS is given, all exceptions will be eaten.
                    Note 2: Passing the max_to_eat_before_throw_up for a given exception type will still lead to a throw up.
            max_to_eat_before_throwing_up: The max exceptions of a given type to eat before throwing up
            throw_up_action: A callable to call when throwing up. The callable should take one arg (a CombinedException).
                If None is given, raise the CombinedException.
            side_dish_action: A callable to call when attempting to eat an exception. Note that performing the side_dish_action does
                not guarantee that a throw_up_action will not be called soon after. The callable should take one arg: an ExceptionInfo.
            digest_time: A timedelta that it should take a caught exception to take to 'digest'. If an exception is digested, it will be
                forgotten and not thrown up (as in it will no longer count towards the max_to_eat_before_throwing_up). By default None is
                given which means no Exception will be 'digested'/forgotten.
            digest_action: A callable to call when digesting an exception. If given, the callable should take one arg: an ExceptionInfo.
        """
        self.exception_types_to_eat = (
            exception_types_to_eat
            if isinstance(exception_types_to_eat, (list, set))
            else [exception_types_to_eat]
        )
        self.max_to_eat_before_throw_up = max_to_eat_before_throw_up
        self.throw_up_action = throw_up_action
        self.side_dish_action = side_dish_action
        self.digest_time = digest_time
        self.digest_action = digest_action
        self._exception_information = collections.defaultdict(list)

    def _is_eating_all_exceptions(self):
        return self.ALL_EXCEPTIONS in self.exception_types_to_eat

    def __enter__(self):
        return self

    def _check_and_perform_digestion(self, typ: typing.Type, now: datetime.datetime):
        """
        Checks the currently saved exceptions for the given type and removes once that expired based
        off the digest_time. Will also call the digest_action if given.
        """
        if self.digest_time is not None:
            new_ex_infos = []
            for ex_info in self._exception_information[typ]:
                ex_info = typing.cast(ExceptionInfo, ex_info)
                if (now - ex_info.time_stamp) >= self.digest_time:
                    if self.digest_action is not None:
                        self.digest_action(ex_info)
                else:
                    new_ex_infos.append(ex_info)

            self._exception_information[typ] = new_ex_infos

    def __exit__(self, typ, value, traceback):
        if (
            typ not in self.exception_types_to_eat
            and not self._is_eating_all_exceptions()
        ) or value is None:
            # about to raise a not eaten exception OR there is no exxception
            return

        now = datetime.datetime.now()
        ex_info = ExceptionInfo(value, traceback, now)
        self._exception_information[typ].append(ex_info)

        # check all current exception_information for if it should be digested
        self._check_and_perform_digestion(typ, now)

        if self.side_dish_action is not None:
            self.side_dish_action(ex_info)

        if len(self._exception_information[typ]) > self.max_to_eat_before_throw_up:
            # define class here so it subclasses the type of the raised exception
            class FullCombinedException(CombinedException, typ):
                pass

            raise_list = self._exception_information[typ]
            self._exception_information[typ] = []

            ex = FullCombinedException(raise_list)
            if self.throw_up_action is None:
                raise ex
            else:
                self.throw_up_action(ex)

        # if we get here, do not throw anything
        return True
