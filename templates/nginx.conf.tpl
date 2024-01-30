worker_processes  2;
user              nginx;

events {
    use           epoll;
    worker_connections  128;
}

error_log         /var/log/nginx/error.log info;

http {
    server_tokens off;
    include       /etc/nginx/mime.types;

    access_log    /var/log/nginx/access.log  combined;

    server {
        server_name   localhost;
        listen        8080;

        {% for ip in blocked_ips %}
        deny {{ ip }};
        {% endfor %}

        location      / {
        	proxy_pass $scheme://$host:$server_port$app_destination;
        }

    }
}
