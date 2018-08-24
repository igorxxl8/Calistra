from tests.json_tests import JsonTests
from tests.queues_tests import QueueTests
from tests.task_tests import TaskTests
from tests.plans_tests import PlanTests
from tests.users_tests import UserTests

jt = JsonTests()
jt.test_array_1_to_json()

tt = TaskTests()

qt = QueueTests()

pt = PlanTests()

ut = UserTests()
