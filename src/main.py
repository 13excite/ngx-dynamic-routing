import argparse
import re
import sys

from ngxfmt import format_config_contents

from jinja2 import Template

# path to the template file
TEMPLATE_PATH = "templates/nginx.conf.tpl.j2"

MAX_NGX_WORKER = 8
NGX_USER = "root"

DEFAULT_DST_LOCATION="/default-route/"
DEFAULT_APP_ROOT_DIR = "/usr/share/nginx/html/"


def validate_default_destination_location(default_destination_location):
    """Validate the default destination location"""
    pattern = re.compile(r'^\/[a-z0-9-]{3,15}\/$')
    if pattern.match(default_destination_location):
        return True
    return False


def validate_app_root_dir(app_root_dir):
    """Validate the app root directory"""
    pattern = re.compile(r'^((/[a-zA-Z0-9-_]+)+/|/)$')
    if pattern.match(app_root_dir):
        return True
    return False


def generate_nginx_config(template_struct):
    with open(TEMPLATE_PATH, 'r', encoding="utf-8") as file:
        template_content = file.read()

    template = Template(template_content)
    nginx_config = template.render({
        "base_struct" : template_struct,
        })

    return nginx_config


def write_nginx_config(nginx_config, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(nginx_config)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--out', type=str,
                        default="nginx_dynamic_routes.conf",
                        help='usage (-o|--out) output file name',
                        required=False
                        )
    parser.add_argument('-l', '--default-location', type=str,
                        default=DEFAULT_DST_LOCATION,
                        help='default static location',
                        required=False
                        )
    parser.add_argument('-w', '--worker', type=int,
                        default=2,
                        help='ngx worker process',
                        required=False
                        )
    parser.add_argument('-u', '--user', type=str,
                    default=NGX_USER,
                    help='ngx user',
                    required=False
                    )
    parser.add_argument('-d', '--app-root-dir', type=str,
                    default=DEFAULT_APP_ROOT_DIR,
                    help='default directory for the app static files',
                    required=False
                    )

    args = parser.parse_args()

    nginx_templates_struct = {
        # List of IP addresses to block
        "blocked_ips" : ["192.168.1.1", "10.0.0.5"],
        # routes based on the query parameter
        "dynamic_routes_map" : {
            1 : '/app1',
            2 : '/app2',
        },
        # default location and var name for the default route
        "default_destination_location": {
            "name": "default_destination",
            "value": DEFAULT_DST_LOCATION,
            "alias": "/usr/share/nginx/html/default/"
        },
        # default proxy cache options
        "proxy_cache": {
            "path": "/tmp",
            "keys_zone_name": "STATIC",
            "keys_zone_size": "10m",
            "inactive": "1h",
            "max_size": "10m",
            "min_uses": 2,
        },
        "worker": 2,
        "user": NGX_USER,
        "app_root_dir": DEFAULT_APP_ROOT_DIR,
        "keepalive_timeout": 400,
    }

    # Validate the default destination location and update the value
    if args.default_location != DEFAULT_DST_LOCATION:
        if not validate_default_destination_location(args.default_location):
            print(r"Invalid default destination location. Must be match the pattern: ^\/[a-z0-9-]{3,15}/$")
            sys.exit(1)
        nginx_templates_struct["default_destination_location"]["value"] = args.default_location

    # Validate the worker process and update the value
    if args.worker not in range(1, MAX_NGX_WORKER+1):
        print(f'Invalid worker process. Must be in range 1-{MAX_NGX_WORKER}')
        sys.exit(1)
    nginx_templates_struct["worker"] = args.worker

    # update the user if it is not the default
    if args.user != NGX_USER:
        nginx_templates_struct["user"] = args.user

    # update the app root directory if it is not the default
    if args.app_root_dir != DEFAULT_APP_ROOT_DIR:
        if not validate_app_root_dir(args.app_root_dir):
            print("Invalid app root directory. Must be match the pattern: ^((/[a-zA-Z0-9-_]+)+/|/)$")
            sys.exit(1)
        nginx_templates_struct["app_root_dir"] = args.app_root_dir

    # Generate Nginx configuration
    formated_ngx_config = format_config_contents(
        generate_nginx_config(nginx_templates_struct),
        exclude_patterns=[]
    )
    # and write to file
    write_nginx_config(formated_ngx_config, args.out)


if __name__ == '__main__':
    main()
