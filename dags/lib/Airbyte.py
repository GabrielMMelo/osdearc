import requests


class AirbyteAPI():
    # TODO: use default e-mail as the airflow admin user email
    def __init__(self, host="localhost", port=8888, ssl=False):
        self.host = host
        self.port = port
        self.ssl = ssl
        self.url = "".join(["https://" if self.ssl else "http://", self.host, ":", str(self.port)])

    def source_exists(self, source_name: str) -> str:
        """Check if a given source_name (By default, the dag's id) exists in airbyte. Returns the id, if it exists"""
        list_sources_endpoint = "/api/v1/sources/list"
        list_sources_url = self.url + list_sources_endpoint
        sources = requests.post(list_sources_url, headers={'Content-Type': "application/json"})
        response = sources.json()
        sourceId = list(filter(lambda x: x["name"] == source_name, response.get("sources")))[0].get("sourceId")
        return sourceId

    # TODO: change it for a more reliable approach
    def get_workspace_id_by_email(self, email):
        """Get workspace id by a given email (NOTE: its a temporary approach)"""
        list_workspaces_endpoint = "/api/v1/workspaces/list"
        list_workspaces_url = self.url + list_workspaces_endpoint
        workspaces = requests.post(list_workspaces_url, headers={'Content-Type': "application/json"})
        response = workspaces.json()
        workspace_id = list(filter(lambda x: x["email"] == email, response.get("workspaces")))[0].get("workspaceId")
        return workspace_id

    def get_source_definition_id_by_repository(self, repository):
        """Get source definition id by DockerHub repository name."""
        list_source_definitions_endpoint = "/api/v1/source_definitions/list"
        list_source_definitions_url = self.url + list_source_definitions_endpoint
        source_definitions = requests.post(list_source_definitions_url, headers={'Content-Type': "application/json"})
        response = source_definitions.json()
        source_definition_id = \
            list(
                filter(lambda x: x["dockerRepository"] == repository, response.get("sourceDefinitions")))[
                0].get(
                "sourceDefinitionId")
        return source_definition_id

    def create_source(self, name, source_name, workspace_id, source_definition_id, connection_configuration):
        """Create a source in Airbyte."""
        body = {
            "sourceDefinitionId": source_definition_id,
            "workspaceId": workspace_id,
            "connectionConfiguration": connection_configuration,
            "name": name,
            "sourceName": source_name
        }

        create_sources_endpoint = "/api/v1/sources/create"
        create_sources_url = self.url + create_sources_endpoint
        source_creation = requests.post(create_sources_url, body=body, headers={'Content-Type': "application/json"})
        response = source_creation.json()
        return response

