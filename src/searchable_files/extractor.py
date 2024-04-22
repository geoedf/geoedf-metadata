import datetime
import fnmatch
import hashlib
import json
import os
import re
import shutil
import uuid

import click
import ruamel.yaml
from identify import identify

from .extract.converter import RESOURCE_URL_PREFIX, SITE_URL_PREFIX, get_creator, get_spatial_coverage, \
    get_identifier_list
from .extract.extract_metadata import extract_metadata
from .lib import all_filenames, common_options, prettyprint_json

yaml = ruamel.yaml.YAML(typ="safe")


class FileMetadata:
    def __init__(self, filename, file_uuid, creator_info, settings):
        self.filename = filename
        self.settings = settings
        self._uuid = file_uuid
        self._creator_info = creator_info

        self._name = os.path.basename(self.filename)
        self._size = os.stat(self.filename).st_size
        self._date_created = datetime.datetime.fromtimestamp(os.stat(self.filename).st_mtime).isoformat()
        self._date_modified = datetime.datetime.fromtimestamp(os.stat(self.filename).st_mtime).isoformat()
        self._date_published = datetime.datetime.now().isoformat()
        self._tags = list(identify.tags_from_path(self.filename))
        self._extension = extension(self.filename)
        self._preview = read_head(self.filename, self.settings)

        # resource properties
        self._url = None
        self._description = None
        self._spatial_coverage = None
        self._temporal_coverage = None
        self._identifier = None
        self._download_url = None

    @property
    def uuid(self):
        return self._uuid

    @property
    def name(self):
        return self._name

    @property
    def size(self):
        return self._size

    @property
    def date_created(self):
        return self._date_created

    @property
    def date_modified(self):
        return self._date_modified

    @property
    def date_published(self):
        return self._date_published

    @property
    def tags(self):
        return self._tags

    @property
    def extension(self):
        return self._extension

    @property
    def preview(self):
        return self._preview

    @property
    def creator_info(self):
        return self._creator_info

    @creator_info.setter
    def creator_info(self, value):
        self._creator_info = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def spatial_coverage(self):
        return self._spatial_coverage

    @spatial_coverage.setter
    def spatial_coverage(self, value):
        self._spatial_coverage = value

    @property
    def temporal_coverage(self):
        return self._temporal_coverage

    @temporal_coverage.setter
    def temporal_coverage(self, value):
        self._temporal_coverage = value

    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, value):
        self._identifier = value

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

    @property
    def download_url(self):
        return self._download_url

    @download_url.setter
    def download_url(self, value):
        self._download_url = value

    def update_metadata(self, idata_metadata):
        self.spatial_coverage = get_spatial_coverage(idata_metadata)
        self.url = f'{RESOURCE_URL_PREFIX}/{self.uuid}'
        self.identifier = get_identifier_list(idata_metadata, self.uuid)
        self.download_url = f'{SITE_URL_PREFIX}/api/resource/download/{self.uuid}'
        return None

    def to_dict(self):
        return {
            "name": self.name,
            "size": self.size,
            "modification_time": self.date_modified,
            "tags": self.tags,
            "extension": self.extension,
            "preview": self.preview,
            "uuid": self.uuid
        }

    def to_schemaorg(self):
        creator_schemaorg = get_creator(self.creator_info)

        schemaorg_json = {
            "@context": "https://schema.org",
            "@id": self.uuid,  # should be a url?
            "sameAs": self.url,
            "url": self.url,

            "@type": "Dataset",
            # "additionalType": "link",
            "name": self.name,
            "description": f'This publication {self.name} is a resource in GeoEDF Portal. ',
            "keywords": ["Keyword1", "Keyword2", "Keyword3"],
            "creativeWorkStatus": "Published",
            # "inLanguage": "en-US",

            "identifier": self.identifier,
            "creator": creator_schemaorg,
            "temporalCoverage": "2018-05-24/2019-06-24",
            "spatialCoverage": self.spatial_coverage,
            "publisher": {
                "@type": "Organization",
                "name": "Purdue University"
            },
            "provider": {
                "@id": SITE_URL_PREFIX,
                "@type": "Organization",
                "name": "GeoEDF Portal",
                "url": SITE_URL_PREFIX,
            },
            "includedInDataCatalog": {
                "@type": "DataCatalog",
                "name": "GeoEDF",
                "url": f'{SITE_URL_PREFIX}'
            },
            "dcat:landingPage": {
                "@id": self.url,
            },
            "license": {
                "@type": "CreativeWork",
                "text": "This resource is shared under the Creative Commons Attribution CC BY.",
                "url": "http://creativecommons.org/licenses/by/4.0/"
            },

            "isAccessibleForFree": True,
            "dateModified": self.date_modified,
            "datePublished": self.date_published,
            "subjectOf": {
                "@type": "DataDownload",
                "name": "resourcemetadata.xml",
                "description": "Description about the dataset",
                "url": self.url,
                "encodingFormat": "application/rdf+xml"
            },
            "distribution": {
                "@type": "DataDownload",
                "contentSize": "46.4 MB",
                "encodingFormat": "application/zip",
                "contentUrl": f'{self.download_url}',
                "identifier": [self.url]
            }
        }

        return schemaorg_json

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)


def file_tags(filename):
    return list(identify.tags_from_path(filename))


def stat_dict(filename):
    info = os.stat(filename)
    return {
        "mode": oct(info.st_mode),
        "size_bytes": info.st_size,
        "mtime": datetime.datetime.fromtimestamp(info.st_mtime).isoformat(),
    }


def extension(filename):
    if "." in filename:
        return filename.split(".")[-1]
    return None


def read_head(filename, settings):
    match = False
    for pattern in settings.read_head["files"]:
        if fnmatch.fnmatch(filename, pattern):
            match = True

    if not match:
        return None

    # read 2x the desired length of data (to handle preamble matches below)
    #
    # note that this is not necessarily 'head_length' bytes
    # e.g. if the file is encoded in utf-8, 1 character can be up to 4 bytes
    with open(filename) as fp:
        data = fp.read(settings.head_length * 2)
    # once the data is read, check it against any skip_preamble_patterns to see
    # if there is a match
    # and if so, take data starting after that match
    for pattern in settings.skip_preamble_patterns:
        match = pattern.search(data)
        if match:
            return data[match.end():][: settings.head_length]
    # if there was no match, truncate down to the correct length
    return data[: settings.head_length]


def get_basic_info(filename, settings, uuid):
    info = os.stat(filename)

    return {
        "tags": file_tags(filename),
        "extension": extension(filename),
        "name": os.path.basename(filename),
        "identifier": uuid,
        "title": os.path.basename(filename),
        "dateCreated": datetime.datetime.fromtimestamp(info.st_mtime).isoformat(),
        "dateModified": datetime.datetime.fromtimestamp(info.st_mtime).isoformat(),
        "description": get_description(filename, settings),
    }


def get_description(filename, settings):
    if read_head(filename, settings) is None:
        return f'This publication {os.path.basename(filename)} is a resource in GeoEDF Portal. '
    return read_head(filename, settings)


def filename2dict(file_uuid, filename, settings, creator_info):
    print("\n===========\nfilename: " + filename)
    info = os.stat(filename)
    if file_uuid is None:
        file_uuid = str(uuid.uuid4())

    file_metadata = FileMetadata(filename, file_uuid, creator_info, settings)
    if creator_info is not None:
        file_metadata.creator = get_creator(creator_info)
    schemaorg_json_obj = metadata2schemaorg(file_metadata)
    # schemaorg_json_obj_static = metadata2schemaorg_static(filename, settings)
    return {
        "relpath": file_metadata.filename,
        **stat_dict(filename),
        "head": file_metadata.preview,
        "tags": file_metadata.tags,
        "extension": file_metadata.extension,
        "name": file_metadata.name,
        "identifier": file_uuid,
        "title": os.path.basename(filename),
        "dateCreated": file_metadata.date_created,
        "dateModified": file_metadata.date_modified,
        "description": get_description(filename, settings),
        "basicInfo": get_basic_info(filename, settings, file_uuid),
        "subject": file_uuid,
        # schemaorg json
        "schemaorgJson": schemaorg_json_obj,
    }


def multiplefile2dict(file_uuid, path, settings, publication_name, description, keywords, creator):
    print("\n===========\npath: " + path)

    if file_uuid is None:
        file_uuid = str(uuid.uuid4())

    old_cwd = os.getcwd()
    os.chdir(path)

    rendered_data = {}
    merged_data = None
    merged_schemaorg = None
    merged_has_part = []
    # in all_filenames("single_files")
    for filename in all_filenames("."):
        rendered_data[filename] = filename2dict(file_uuid, filename, settings, creator)
        if merged_data is None:
            merged_data = rendered_data[filename]
        if "schemaorgJson" in merged_data:
            if merged_schemaorg is None:
                merged_schemaorg = merged_data['schemaorgJson']
            merged_has_part.append(get_sub_data(rendered_data[filename]['schemaorgJson']))
    merged_schemaorg['hasPart'] = merged_has_part

    # pattern = "[^/\\]+[/\\]*$"
    # name = re.search(pattern, path).
    name = os.path.basename(path)
    merged_schemaorg['name'] = name
    if publication_name is not None:
        merged_schemaorg['name'] = publication_name
        merged_data['title'] = publication_name
        merged_data['basicInfo']['title'] = publication_name

    if description is not None:
        merged_schemaorg['description'] = description
        merged_data['description'] = description
        merged_data['basicInfo']['description'] = description

    if keywords is not None:
        merged_schemaorg['keywords'] = keywords

    merged_data['schemaorgJson'] = merged_schemaorg
    merged_data['relpath'] = path
    merged_data['name'] = publication_name
    merged_data.pop('size_bytes')

    return merged_data


def get_sub_data(schemaorg_data):
    return {
        "@type": "Dataset",
        "name": schemaorg_data['name'],
        "description": schemaorg_data['description'],
        "license": schemaorg_data['license'],
        "creator": schemaorg_data['creator'],
        "url": RESOURCE_URL_PREFIX,
    }


def metadata2schemaorg(file_metadata: FileMetadata):
    idata_metadata = extract_metadata(file_metadata.filename)
    print(json.dumps(idata_metadata))

    file_metadata.update_metadata(idata_metadata)
    return file_metadata.to_schemaorg()
    # return idata2schemaorg(file_metadata.filename, idata_metadata, file_metadata.uuid, file_metadata.creator_info,
    #                        file_metadata.settings)


def target_file(output_directory, filename):
    hashed_name = hashlib.sha256(filename.encode("utf-8")).hexdigest()
    os.makedirs(output_directory, exist_ok=True)
    return os.path.join(output_directory, hashed_name) + ".json"


class Settings:
    def __init__(self, settingsdict):
        self.read_head = settingsdict.get("read_head", {})
        self.source_path = settingsdict.get("source_path", {})
        self.output_path = settingsdict.get("output_path", {})
        if "files" not in self.read_head:
            self.read_head["files"] = []
        self.head_length = int(self.read_head["length"])
        patterns = self.read_head.get("skip_preamble_patterns", [])
        self.skip_preamble_patterns = [re.compile(p) for p in patterns]


def _load_settings_callback(ctx, param, value):
    if value is not None:
        print(f'fp = {value}', value)
        with open(value) as fp:
            return Settings(yaml.load(fp))


@click.command(
    "extract",
    help="Extract metadata from a directory.\n"
         "This command creates per-file metadata from a directory of files. "
         "Stat data like mode and mtime, the first 100 characters, and the "
         "detected filetype are all used",
)
@click.option(
    "--directory",
    default="data/files/single_file",
    show_default=True,
    help="A path, relative to the current working directory, "
         "containing data files from which to extract metadata",
)
@click.option(
    "--clean",
    default=False,
    is_flag=True,
    help="Empty the output directory before writing any data there",
)
@click.option(
    "--output",
    default="output/extracted",
    show_default=True,
    help="A path, relative to the current working directory, "
         "where the extracted metadata should be written",
)
@click.option(
    "--settings",
    default="data/config.yaml/extractor.yaml",
    show_default=True,
    callback=_load_settings_callback,
    help="YAML file with configuration for the extractor",
)
@common_options
def extract_cli(settings, directory, output, clean):
    clean = True
    if clean:
        shutil.rmtree(output, ignore_errors=True)

    old_cwd = os.getcwd()
    os.chdir(directory)

    rendered_data = {}
    # in all_filenames("single_files")
    for filename in all_filenames("."):
        # name, ext = os.path.splitext(filename)
        # print(name + ", " + ext + ".")

        rendered_data[filename] = filename2dict(None, filename, settings)

    # in all_filenames("multiple_files")
    # generate schemaorg for each file
    # generate schemaorg for the zip file
    # add schemaorg of each file to the 'hasPart' field in the schemaorg of the zip file

    os.chdir(old_cwd)
    for filename, data in rendered_data.items():
        with open(target_file(output, filename), "w") as fp:
            prettyprint_json(data, fp)

    click.echo("metadata extraction complete")
    click.echo(f"results visible in\n  {output}")


SETTING_PATH = "data/config/extractor.yaml"


def extract_handler(uuid, publication_name, path, clean, file_type, description, keywords, user_email):
    settings = Settings(yaml.load(open(SETTING_PATH)))
    output = settings.output_path

    if clean:
        shutil.rmtree(output, ignore_errors=True)

    old_cwd = os.getcwd()
    # os.chdir(directory)
    print(f"[extract_handler] settings={settings}")
    # identifier = get_identifier_list(data, file_uuid)
    creator_info = {
        "email": user_email,
        # "name": "", # get name from cilogon?
    }

    rendered_data = {}
    # in all_filenames("single_files")
    if file_type == "single":
        rendered_data[path] = filename2dict(uuid, path, settings, creator_info)
    elif file_type == "multiple":
        rendered_data[path] = multiplefile2dict(uuid, path, settings, publication_name, description, keywords,
                                                creator_info)
    elif file_type == "list":
        path_list = path
        for p in path_list:
            rendered_data[path] = filename2dict(uuid, p, settings, creator_info)

    os.chdir(old_cwd)
    for filename, data in rendered_data.items():
        with open(target_file(output, filename), "w") as fp:
            prettyprint_json(data, fp)

    click.echo("metadata extraction complete")
    click.echo(f"results visible in\n  {output}")
    return
