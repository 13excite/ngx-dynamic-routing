from jinja2 import Template


def generate_nginx_config(blocked_ips, _):
    with open('templates/nginx.conf.tpl', 'r') as file:
        template_content = file.read()

    template = Template(template_content)
    nginx_config = template.render({"blocked_ips" : blocked_ips})

    return nginx_config


def write_nginx_config(nginx_config):
    with open("nginx_dynamic_routes.conf", "w") as f:
        f.write(nginx_config)


if __name__ == '__main__':

    # routes based on the query parameter
    dynamic_routes = { 1 : '/app1',
                       2 : '/app2' }

    # List of IP addresses to block
    blocked_ips = ["192.168.1.1", "10.0.0.5"]

    # Generate Nginx configuration
    nginx_config = generate_nginx_config(blocked_ips, dynamic_routes)
    write_nginx_config(nginx_config)
