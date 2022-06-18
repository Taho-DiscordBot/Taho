from sshtunnel import SSHTunnelForwarder

__all__ = (
    "init_ssh_tunnel",
)

def init_ssh_tunnel(config: dict=None) -> SSHTunnelForwarder:
    if not config:
        from ... import config as _config
        config = vars(_config)
    return SSHTunnelForwarder(
        (config["SSH_HOST"], config["SSH_PORT"]),
        ssh_username=config["SSH_USERNAME"],
        ssh_password=config["SSH_PASSWORD"],
        remote_bind_address=(config["SSH_REMOTE_HOST"], config["SSH_REMOTE_PORT"]),
    )

