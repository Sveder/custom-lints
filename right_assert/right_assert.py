import astroid

from pylint.checkers import BaseChecker, utils
from pylint.interfaces import IAstroidChecker


BASE_ID = 99


def register_checkers(linter):
    """Register checkers."""
    linter.register_checker(AssertChecker(linter))

register = register_checkers

class AssertChecker(BaseChecker):
    __implements__ = (IAstroidChecker,)

    AFFECTED_ASSERTS = ["assertTrue", "assertFalse"]

    USE_ASSERT_EQUAL = 'wrong-assert-should-be-assertequal'
    USE_ASSERT_IN = 'wrong-assert-should-be-assertin'
    USE_ASSERT_COMPARE = 'wrong-assert-should-be-assertcomparison'
    msgs = { 'C%d20' % BASE_ID: ("%s is a comparison, use assertEqual.", USE_ASSERT_EQUAL, "moooo",),
             'C%d21' % BASE_ID: ("%s is an in statement, use assertIn.", USE_ASSERT_IN, "moooo",),
             'C%d22' % BASE_ID: ("%s is a comparison, use assertGreater or assertLess.", USE_ASSERT_COMPARE, "moooo",)
    }

    name = 'assert-checker'

    @utils.check_messages(USE_ASSERT_EQUAL, USE_ASSERT_IN)
    def visit_callfunc(self, node):
        if not isinstance(node.func, astroid.Getattr):
            # It isn't a getattr ignore this. All the assertMethods are attrs of self:
            return

        if not node.func.attrname in self.AFFECTED_ASSERTS:
            # Not an attribute / assert we care about
            return

        first = node.args[0]
        if not isinstance(first, astroid.Compare):
            # Not a comparer, so this is probably ok:
            return

        if first.ops[0][0] == "==":
            # An assertTrue with a compare should be assertEqual:
            self.add_message(self.USE_ASSERT_EQUAL, args=first.as_string(), node=node)

        if first.ops[0][0] == "in":
            # An assertTrue with an in statement should be assertIn:
            self.add_message(self.USE_ASSERT_IN, args=first.as_string(), node=node)

        if "<" in first.ops[0][0] or ">" in first.ops[0][0]:
            # An assertTrue with a comparison should be assertGreater or assertLess:
            self.add_message(self.USE_ASSERT_COMPARE, args=first.as_string(), node=node)