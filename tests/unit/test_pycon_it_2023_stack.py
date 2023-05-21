import aws_cdk as core
import aws_cdk.assertions as assertions

from pycon_it_2023.pycon_it_2023_stack import PyconIt2023Stack

# example tests. To run these tests, uncomment this file along with the example
# resource in pycon_it_2023/pycon_it_2023_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = PyconIt2023Stack(app, "pycon-it-2023")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
