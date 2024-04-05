import datetime
import os

RESOURCE_URL_PREFIX = "https://geoedf-portal.anvilcloud.rcac.purdue.edu/resource"
SITE_URL_PREFIX = "https://geoedf-portal.anvilcloud.rcac.purdue.edu"
AFFILIATION_NAME = "Purdue University"
CREATOR_NAME = "Yiqing Qu"
CREATOR_EMAIL = "qu112@purdue.edu"


def idata2schemaorg(filename, data, file_uuid, settings):
    info = os.stat(filename)
    # print(data)
    spatial_coverage = get_spatial_coverage(data)
    # print("spatial_coverage" + str(spatial_coverage))
    creator = get_creator(data, AFFILIATION_NAME, CREATOR_NAME, CREATOR_EMAIL, None)
    identifier = get_identifier_list(data, file_uuid)
    download_url = f'{SITE_URL_PREFIX}/api/resource/download/{file_uuid}'

    schemaorg_json = {
        "@context": "https://schema.org",
        "@id": file_uuid,  # should be a url
        "sameAs": f'{RESOURCE_URL_PREFIX}/{file_uuid}',
        "url": f'{RESOURCE_URL_PREFIX}/{file_uuid}',

        "@type": "Dataset",
        # "additionalType": "link",
        "name": os.path.basename(filename),
        "description": f'This publication {os.path.basename(filename)} is a resource in GeoEDF Portal. ',
        # "description": read_head(filename, settings),
        "keywords": ["Keyword1", "Keyword2", "Keyword3"],

        "creativeWorkStatus": "Published",

        # "inLanguage": "en-US",

        "identifier": identifier,

        "creator": creator,

        "temporalCoverage": "2018-05-24/2019-06-24",

        "spatialCoverage": spatial_coverage,

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
            "@id": f'{RESOURCE_URL_PREFIX}/{file_uuid}',
        },
        "license": {
            "@type": "CreativeWork",
            "text": "This resource is shared under the Creative Commons Attribution CC BY.",
            "url": "http://creativecommons.org/licenses/by/4.0/"
        },
        # "license": "http://creativecommons.org/licenses/by/4.0/",  # todo some other has a slice

        "isAccessibleForFree": True,
        "dateModified": datetime.datetime.fromtimestamp(info.st_mtime).isoformat(),
        "datePublished": datetime.datetime.now().isoformat(),
        "subjectOf": {
            "@type": "DataDownload",
            "name": "resourcemetadata.xml",
            "description": "Description about the dataset",
            "url": f'{RESOURCE_URL_PREFIX}/{file_uuid}',
            "encodingFormat": "application/rdf+xml"
        },
        "distribution": {
            "@type": "DataDownload",
            "contentSize": "46.4 MB",
            "encodingFormat": "application/zip",
            "contentUrl": f'{download_url}',
            "identifier": [f'{RESOURCE_URL_PREFIX}/{file_uuid}']
        }
    }

    return schemaorg_json


def get_spatial_coverage(data):
    if data is None:
        return None

    spatial_data_fields = ['southlimit', 'westlimit', 'northlimit', 'eastlimit', ]
    # spatial_data_fields = ['latmin', 'lonmin', 'latmax', 'lonmax', ]
    # todo lat lon
    for field in spatial_data_fields:
        if field not in data:
            return None

    box = '%f %f %f %f' % (
        # data['latmin'], data['lonmin'], data['latmax'], data['lonmax'])
        data['southlimit'], data['westlimit'], data['northlimit'], data['eastlimit'])

    return {  # todo: two kinds of coverage, point/shape
        "@type": "Place",
        "geo": {
            "@type": "GeoShape",
            "box": box
        }
    }


def get_identifier_list(data, file_uuid):
    # return [f'{RESOURCE_URL_PREFIX}/{file_uuid}']  # todo check the form of identifier

    if data is None:
        return [{
            "@type": "PropertyValue",
            "url":f'{RESOURCE_URL_PREFIX}/{file_uuid}',
            "@id":  file_uuid,
            "name": f'{RESOURCE_URL_PREFIX}/{file_uuid}'
        }]
        # return [f'{RESOURCE_URL_PREFIX}/{file_uuid}']
    identifier = {
        "@type": "PropertyValue",
    }
    if "identifier" in data:
        identifier['name'] = data['identifier']  # want to test if `filename` is the wrong key name
    if "id" in data:
        identifier['@id'] = data['id']
    if "url" in data:
        identifier['url'] = f'{RESOURCE_URL_PREFIX}/{file_uuid}'
    return [identifier]


def get_creator(data, affiliation, name, email, url):
    if url is None:
        url = SITE_URL_PREFIX + "/accounts/profile/"
    return {
        "@list": [
            {
                "@type": "Person",
                "affiliation": {
                    "@type": "Organization",
                    "name": affiliation,
                },
                "email": email,
                "name": name,
                "url": url,
            }
        ]
    }
