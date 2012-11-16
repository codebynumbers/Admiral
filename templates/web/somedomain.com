server {
    server_name somedomain.com;
    access_log  /var/log/nginx/somedomain.access.log;
    location / {
        root   /home/somedomain;
        index  index.html index.htm index.php;
    }
}
