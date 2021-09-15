import json
import logging
import requests


class AirbyteAPI():
    def __init__(self, host="localhost", port=8888, ssl=False):
        self.host = host
        self.port = port
        self.ssl = ssl
        self.url = "".join(["https://" if self.ssl else "http://", self.host, ":", str(self.port)])

    # TODO: change it for a more reliable approach
    def get_workspace_id_by_email(self, email):
        """Get workspace id by a given email (NOTE: its a temporary approach)"""
        list_workspaces_endpoint = "/api/v1/workspaces/list"
        list_workspaces_url = self.url + list_workspaces_endpoint
        response = requests.post(list_workspaces_url, headers={'Content-Type': "application/json"})
        workspaces = response.json()
        logging.debug(workspaces)
        workspace_id = list(filter(lambda x: x["email"] == email, workspaces.get("workspaces")))[0].get("workspaceId")
        return workspace_id

    def get_source_by_name(self, workspace_id: str, source_name: str) -> bool:
        """Check if a given source_name (By default, the dag's id) exists in airbyte. Returns the id, if it exists"""
        list_sources_endpoint = "/api/v1/sources/list"
        list_sources_url = self.url + list_sources_endpoint
        data = {
            "workspaceId": workspace_id
        }
        response = requests.post(list_sources_url, data=json.dumps(data), headers={'Content-Type': "application/json"})
        sources = response.json()
        logging.debug(sources)
        try:
            source = list(filter(lambda x: x["name"] == source_name, sources.get("sources")))[0]
        except IndexError:
            return None

        return source.get("sourceId", None)

    def get_source_definition_id_by_repository(self, repository):
        """Get source definition id by DockerHub repository name."""
        list_source_definitions_endpoint = "/api/v1/source_definitions/list"
        list_source_definitions_url = self.url + list_source_definitions_endpoint
        response = requests.post(list_source_definitions_url, headers={'Content-Type': "application/json"})
        source_definitions = response.json()
        logging.debug(source_definitions)
        source_definition_id = \
            list(
                filter(lambda x: x["dockerRepository"] == repository, source_definitions.get("sourceDefinitions")))[
                0].get(
                "sourceDefinitionId")
        return source_definition_id

    def create_source(self, name, workspace_id, source_definition_id, connection_configuration):
        """Create a source in Airbyte."""
        data = {
            "sourceDefinitionId": source_definition_id,
            "workspaceId": workspace_id,
            "connectionConfiguration": connection_configuration,
            "name": name
        }

        create_sources_endpoint = "/api/v1/sources/create"
        create_sources_url = self.url + create_sources_endpoint
        response = requests.post(create_sources_url, data=json.dumps(data), headers={'Content-Type': "application/json"})
        source = response.json()

        return source.get("sourceId")

    def get_destination_by_name(self, workspace_id: str, destination_name: str) -> str:
        """Check if a given destination_name (By default, the dag's id) exists in airbyte. Returns the id, if it exists"""
        list_destinations_endpoint = "/api/v1/destinations/list"
        list_destinations_url = self.url + list_destinations_endpoint
        data = {
            "workspaceId": workspace_id
        }
        response = requests.post(list_destinations_url, data=json.dumps(data), headers={'Content-Type': "application/json"})
        destinations = response.json()
        logging.debug(destinations)
        try:
            destination = list(filter(lambda x: x["name"] == destination_name, destinations.get("destinations")))[0]
        except IndexError:
            return None

        return destination.get("destinationId", None)

    def get_destination_definition_id_by_repository(self, repository):
        """Get destination definition id by DockerHub repository name."""
        list_destination_definitions_endpoint = "/api/v1/destination_definitions/list"
        list_destination_definitions_url = self.url + list_destination_definitions_endpoint
        response = requests.post(list_destination_definitions_url, headers={'Content-Type': "application/json"})
        destination_definitions = response.json()
        logging.debug(destination_definitions)
        destination_definition_id = \
            list(
                filter(lambda x: x["dockerRepository"] == repository, destination_definitions.get("destinationDefinitions")))[
                0].get(
                "destinationDefinitionId")
        return destination_definition_id

    def create_destination(self, name, workspace_id, destination_definition_id, connection_configuration):
        """Create a destination in Airbyte."""
        data = {
            "destinationDefinitionId": destination_definition_id,
            "workspaceId": workspace_id,
            "connectionConfiguration": connection_configuration,
            "name": name
        }

        create_destinations_endpoint = "/api/v1/destinations/create"
        create_destinations_url = self.url + create_destinations_endpoint
        response = requests.post(create_destinations_url, data=json.dumps(data), headers={'Content-Type': "application/json"})
        destination = response.json()

        return destination.get("destinationId")

    def get_source_stream(self, source_id):
        """Returns source stream, including discovered schema and supported sync methods."""
        data = {
            "sourceId": source_id
        }

        get_stream_endpoint = "/api/v1/sources/discover_schema"
        get_stream_url = self.url + get_stream_endpoint
        response = requests.post(get_stream_url, data=json.dumps(data), headers={'Content-Type': "application/json"})
        catalog = response.json()
        logging.info("Catalog:")
        logging.info(catalog)

        try:
            stream = catalog["catalog"]["streams"][0]["stream"]
        except IndexError:
            return None

        return stream

    def get_connection_by_source_and_destination(self, workspace_id: str, source_id: str, destination_id: str) -> str:
        """Check if a given source_name (By default, the dag's id) exists in airbyte. Returns the id, if it exists"""
        list_connections_endpoint = "/api/v1/connections/list"
        list_connections_url = self.url + list_connections_endpoint
        data = {
            "workspaceId": workspace_id
        }
        response = requests.post(list_connections_url, data=json.dumps(data), headers={'Content-Type': "application/json"})
        connections = response.json()
        logging.info("Connections:")
        logging.info(connections)
        try:
            connection = list(filter(lambda x: x["sourceId"] == source_id and x["destinationId"] == destination_id, connections.get("connections")))[0]
        except IndexError:
            return None

        return connection.get("connectionId", None)

    def create_connection(self, source_id, source_stream, destination_id, configuration_template, schedule=None):
        """Create a connection in Airbyte."""

        logging.info("Source ID: " + source_id)
        logging.info("Destination ID: " + destination_id)

        configuration_template["sourceId"] = source_id
        configuration_template["destinationId"] = destination_id
        configuration_template["syncCatalog"]["streams"][0]["stream"] = source_stream
        configuration_template["schedule"] = schedule

        data = configuration_template
        logging.info("Configuration template: ")
        logging.info(data)

        create_connections_endpoint = "/api/v1/connections/create"
        create_connections_url = self.url + create_connections_endpoint
        connection_creation = requests.post(create_connections_url, data=json.dumps(data), headers={'Content-Type': "application/json"})
        response = connection_creation.json()
        logging.info(response)

        return response.get("connectionId")

    def sync_connection(self, connection_id):
        """Trigger a manual sync for a connection."""
        sync_connections_endpoint = "/api/v1/connections/sync"
        sync_connections_url = self.url + sync_connections_endpoint
        data = {
            "connectionId": connection_id
        }
        response = requests.post(sync_connections_url, data=json.dumps(data),
                                 headers={'Content-Type': "application/json"})
        job = response.json()

        return job.get("job").get("id")

    def get_job_status(self, job_id):
        """Returns the current status from a given job."""
        get_job_endpoint = "/api/v1/jobs/get"
        get_job_url = self.url + get_job_endpoint
        data = {
            "id": job_id
        }
        response = requests.post(get_job_url, data=json.dumps(data),
                                 headers={'Content-Type': "application/json"})
        job = response.json()

        return job.get("job").get("status")
