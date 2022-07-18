import os

class imageScansActions:
    def __init__(self, client):
        self.client = client

    def _get_images(self,repository):
        self.repository = repository
        images_details = self.client.describe_images(repositoryName=self.repository)
        images = []
        for imgdetails in range(len(images_details['imageDetails'])):
            for image in images_details['imageDetails'][imgdetails]['imageTags']:
                images.append(image)
        return(images)

    def _get_all_repositories(self):
        repositories = []
        get_repositories = self.client.describe_repositories()
        for repository in range(len(get_repositories)):
            repositories.append(
                get_repositories['repositories'][repository]['repositoryName'])
        return repositories

    def _scan_images(self, images, repository, ecrurl):
        self.images = images
        self.repository = repository
        self.ecrurl = ecrurl
        for image in self.images:
                command = f"trivy image --format template --template '@reportFormats/html.tpl' -o reports/{image}.html {self.ecrurl}/{self.repository}:{image}"
                os.system(command)
                # return(
                #     f"trivy image --format template --template '@reportFormats/html.tpl' -o reports/{image}.html {self.ecrurl}/{self.repository}:{image}")


    def _list_imageversion_repos(self, image_versions):
        self.image_versions = image_versions
        images_repo = {}
        repositories = imageScansActions._get_all_repositories(self)
        for repository in repositories:
            image = self.client.list_images(repositoryName=repository)
            image_ids = image['imageIds']
            for image_version in self.image_versions:
                for image_id in range(len(image_ids)):
                    if image['imageIds'][image_id]['imageTag'] == image_version :
                        images_repo.update({repository : image['imageIds'][image_id]['imageTag']})

        return images_repo

    def _scan_imageversion_repos(self, image_repos, ecrurl):
        self.image_repos = image_repos
        self.ecrurl = ecrurl
        for repo,image in self.image_repos.items():
            command = f"trivy image --format template --template '@reportFormats/html.tpl' -o reports/{repo}-{image}.html {self.ecrurl}/{repo}:{image}"
            os.system(command)

