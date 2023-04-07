import git
from python_on_whales import docker


def main():
    repo = git.Repo('.')
    current_commit = repo.head.commit

    print(f'Pulling repo, current commit: {current_commit}')
    repo.remotes.origin.pull()
    new_commit = repo.head.commit

    if current_commit == new_commit:
        print('Repo not updated, exiting')
        return False

    print(f'Repo updated to commit: {new_commit}')

    print('Building docker image')
    docker.compose.build()
    print('Docker image built')

    print('Restarting docker containers')
    docker.compose.up(detach=True)
    print('Done')
    return True


if __name__ == '__main__':
    main()
