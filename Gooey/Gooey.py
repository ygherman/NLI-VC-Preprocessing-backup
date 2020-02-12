from gooey import Gooey, GooeyParser


@Gooey(dump_build_config=True, program_name="Visual Culture Preprocessing Tool")
def main():
    desc = "This application encopasses the processes of the VC_Preoprocessing for Ex libris Alma data upload"
    file_help_msg = "Name of the file you want to process"
    parser = GooeyParser(description="My Cool GUI Program!")
    parser.add_argument("FileChooser", help=file_help_msg, widget="FileChooser")
    parser.add_argument('Date', widget="DateChooser")

    args = parser.parse_args()


def here_is_more():
    pass


if __name__ == '__main__':
    main()

# from gooey.python_bindings.gooey_decorator import Gooey
# from gooey.python_bindings.gooey_parser import GooeyParser
#
# @Gooey
# def main():
#     parser = GooeyParser(description='Example validator')
#     parser.add_argument(
#         'secret',
#         metavar='Super Secret Number',
#         help='A number specifically between 2 and 14',
#         gooey_options={
#             'validator': {
#                 'test': '2 <= int(user_input) <= 14',
#                 'message': 'Must be between 2 and 14'
#             }
#         })
#
#     args = parser.parse_args()
#
#     print("Cool! Your secret number is: ", args.secret)
#
#
# if __name__ == '__main__':
#     main()
