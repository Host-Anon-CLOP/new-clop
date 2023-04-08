import click

import git
from python_on_whales import DockerClient


compose_files = {
    'development': './docker-compose.override.yml',
    'test': './docker-compose.test.yml',
    # 'production': './docker-compose.prod.yml',
}

branches = {
    'development': 'dev',
    'test': 'dev',
    # 'production': 'master',
}


@click.command()
@click.option('--environment', '-e', default='development', help='Environment to run in', type=click.Choice(list(compose_files.keys())))
@click.option('--pull/--no-pull', default=True, help='Pull repo before running')
def update_docker_compose(environment, pull):
    repo = git.Repo('.')

    print("Fetching repo")
    repo.remotes.origin.fetch()
    current_commit = repo.head.commit

    branch = branches[environment]
    print(f'Using branch: {branch}')
    current_branch = repo.active_branch.name
    if current_branch != branch:
        print(f'Checking out branch: {branch} from current branch: {current_branch}')
        repo.heads[branch].checkout()

    if pull:
        print(f'Pulling repo, current commit: {current_commit}')
        repo.remotes.origin.pull()
        new_commit = repo.head.commit

        if current_commit == new_commit:
            print('Repo not updated, exiting')
            return False

        print(f'Repo updated to commit: {new_commit}')
    else:
        print('Skipping repo pull')

    compose_file = compose_files[environment]
    print(f'Using compose file: {compose_file} for environment: {environment}')
    docker = DockerClient(compose_files=['./docker-compose.yml', compose_file])

    print('Building docker image')
    docker.compose.build()
    print('Docker image built')

    print('Restarting docker containers')
    docker.compose.up(detach=True)
    print('Done, everything should be up and running now!')
    return True


if __name__ == '__main__':
    update_docker_compose()
