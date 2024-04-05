import json
import os

import click
import ruamel.yaml

from .lib import all_filenames, common_options, search_client, token_storage_adapter
from .lib.search import app_search_client


class Settings:
    def __init__(self, settingsdict):
        self.output_path = settingsdict.get("output_path", "output/submitted")


SETTING_PATH = "data/config/submitter.yaml"

yaml = ruamel.yaml.YAML(typ="safe")


def _load_settings_callback(ctx, param, value):
    if value is not None:
        print(f'fp = {value}', value)
        with open(value) as fp:
            return Settings(yaml.load(fp))


def submit_doc(client, index_id, filename, task_list_file):
    with open(filename) as fp:
        data = json.load(fp)
    res = client.ingest(index_id, data)
    print("res:\n")
    print(res)
    with open(task_list_file, "a") as fp:
        fp.write(res["task_id"] + "\n")


@click.command(
    "submit",
    help="Submit Ingest documents as new Tasks.\n"
         "Reading Ingest documents produced by the Assembler, submit them "
         "each as a new Task and log their task IDs. "
         "These tasks can then be monitored with the `watch` command.",
)
@click.option(
    "--directory",
    default="output/assembled",
    show_default=True,
    help="A path, relative to the current working directory, "
         "containing ingest documents to submit",
)
@click.option(
    "--output",
    default="output/task_submit",
    show_default=True,
    help="A directory relative to the current working directory, "
         "where the resulting task IDs be written",
)
@click.option(
    "--index-id",
    default=None,
    help="Override the index ID where the tasks should be submitted. "
         "If omitted, the index created with `create-index` will be used.",
)
@common_options
def submit_cli(directory, output, index_id):
    client = search_client()

    os.makedirs(output, exist_ok=True)
    task_list_file = os.path.join(output, "tasks.txt")
    with open(task_list_file, "w"):  # empty the file (open in write mode)
        pass

    # ./searchable-files extract && ./searchable-files assemble &&
    # ./searchable-files submit --index-id 76c5e7eb-6cb6-492c-ba80-7e47abff0586 && ./searchable-files watch
    if not index_id:
        index_info = token_storage_adapter().read_config("index_info")
        if index_info is None:
            raise click.UsageError(
                "Cannot submit without first setting up "
                "an index or passing '--index-id'"
            )
        index_id = index_info["index_id"]

    for filename in all_filenames(directory):
        submit_doc(client, index_id, filename, task_list_file)

    click.echo(
        f"""\
ingest document submission (task submission) complete
task IDs are visible in
    {task_list_file}"""
    )


def submit_handler(directory, index_id):
    # initialize client if none
    # client = search_client()
    client = app_search_client()
    settings = Settings(yaml.load(open(SETTING_PATH)))
    output = settings.output_path
    os.makedirs(output, exist_ok=True)

    task_list_file = os.path.join(output, "tasks.txt")
    with open(task_list_file, "w"):  # empty the file (open in write mode)
        pass

    # ./searchable-files extract && ./searchable-files assemble &&
    # ./searchable-files submit --index-id 76c5e7eb-6cb6-492c-ba80-7e47abff0586 && ./searchable-files watch
    if not index_id:
        index_info = token_storage_adapter().read_config("index_info")
        if index_info is None:
            raise click.UsageError(
                "Cannot submit without first setting up "
                "an index or passing '--index-id'"
            )
        index_id = index_info["index_id"]

    print(os.getcwd())
    files = all_filenames(directory)
    for filename in all_filenames(directory):
        print(filename)
        submit_doc(client, index_id, filename, task_list_file)

    click.echo(
        f"""\
ingest document submission (task submission) complete
task IDs are visible in
    {task_list_file}"""
    )
    # print(f'[callback] err_msg={"!!!"}')

    pass
