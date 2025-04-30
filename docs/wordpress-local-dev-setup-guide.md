# WordPress Local Development Setup Guide

This guide helps you run a local WordPress development environment using Docker and import an existing site using All-in-One WP Migration.

## Prerequisites

- Docker and Docker Compose installed
- All-in-One WP Migration backup file (.wpress)
- Terminal/Command Line access

## Step 1: Create Dockerfile

Create a `Dockerfile` with the following content:

```dockerfile
FROM wordpress:6.4
RUN echo "upload_max_filesize=512M" > /usr/local/etc/php/conf.d/custom.ini && \
    echo "post_max_size=512M" >> /usr/local/etc/php/conf.d/custom.ini && \
    echo "memory_limit=512M" >> /usr/local/etc/php/conf.d/custom.ini && \
    echo "max_execution_time=300" >> /usr/local/etc/php/conf.d/custom.ini && \
    echo "max_input_time=300" >> /usr/local/etc/php/conf.d/custom.ini
```

## Step 2: Create Docker Compose File

Create a `docker-compose.yml` file with the following content:

```yaml
services:
  wordpress:
    build: .
    platform: linux/amd64  # For Apple Silicon (M1/M2/M3)
    restart: always
    ports:
      - "8080:80"
    environment:
      WORDPRESS_DB_HOST: db
      WORDPRESS_DB_NAME: ${WP_DB_NAME:-wordpress}
      WORDPRESS_DB_USER: ${WP_DB_USER:-wp_user}
      WORDPRESS_DB_PASSWORD: ${WP_DB_PASSWORD:-wp_password}
      PHP_UPLOAD_MAX_FILESIZE: 512M
      PHP_POST_MAX_SIZE: 512M
      PHP_MEMORY_LIMIT: 512M
      PHP_MAX_EXECUTION_TIME: 300
      PHP_MAX_INPUT_TIME: 300
      WORDPRESS_CONFIG_EXTRA: |
        define('WP_DEBUG', true);
        define('WP_DEBUG_LOG', true);
        define('WP_MEMORY_LIMIT', '512M');
        define('WP_HOME', 'http://localhost:8080');
        define('WP_SITEURL', 'http://localhost:8080');
    volumes:
      - wp_content:/var/www/html/wp-content
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80"]
      interval: 30s
      timeout: 10s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

  db:
    image: mysql:8.0
    platform: linux/amd64
    restart: always
    ports:
      - "127.0.0.1:3306:3306"  # Only allow local connections
    environment:
      MYSQL_DATABASE: ${WP_DB_NAME:-wordpress}
      MYSQL_USER: ${WP_DB_USER:-wp_user}
      MYSQL_PASSWORD: ${WP_DB_PASSWORD:-wp_password}
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-root_password}
    volumes:
      - db_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p${MYSQL_ROOT_PASSWORD:-root_password}"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M

  phpmyadmin:
    image: phpmyadmin:latest
    restart: always
    ports:
      - "127.0.0.1:8081:80"  # Only allow local connections
    environment:
      - PMA_HOST=db
      - PMA_USER=root
      - PMA_PASSWORD=${MYSQL_ROOT_PASSWORD:-root_password}
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD:-root_password}
      - UPLOAD_LIMIT=512M
      - MAX_EXECUTION_TIME=300
    depends_on:
      db:
        condition: service_healthy
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
        reservations:
          cpus: '0.2'
          memory: 256M

networks:
  default:
    name: wordpress_network
    driver: bridge

volumes:
  db_data:
    name: wordpress_db_data
  wp_content:
    name: wordpress_content
```

## Step 3: Create Environment File

Create a `.env` file to store your credentials (optional):

```env
WP_DB_NAME=wordpress
WP_DB_USER=wp_user
WP_DB_PASSWORD=wp_password
MYSQL_ROOT_PASSWORD=root_password
```

## Step 4: Start WordPress Environment

```bash
# Build and start containers
docker-compose up -d --build

# Verify PHP settings
docker exec wordpress php -i | grep -i "upload_max_filesize\|post_max_size\|memory_limit"
```

## Step 5: Access WordPress Setup

1. Open your browser and navigate to `http://localhost:8080`
2. Complete the WordPress installation:
   - Site Title: Your site name
   - Username: admin (or preferred username)
   - Password: Strong password
   - Email: Your email

## Step 6: Install All-in-One WP Migration Plugin

1. Go to WordPress admin → Plugins → Add New
2. Search for "All-in-One WP Migration"
3. Click "Install Now" and then "Activate"

## Step 7: Import Your Backup

1. Go to WordPress admin → All-in-One WP Migration → Import
2. Drag and drop your .wpress file or click "IMPORT FROM" and select your backup
3. Confirm the import when prompted
4. Wait for the import process to complete
5. Click "Finish" when prompted to log in again

## Step 8: Database Access

### Using phpMyAdmin
1. Open `http://localhost:8081`
2. Login with root credentials:
   - Username: root
   - Password: root_password (or value from .env file)

### Using Command Line
```bash
docker exec -it $(docker-compose ps -q db) mysql -u root -p
```

## Troubleshooting

### Permission Issues
```bash
docker exec -it $(docker-compose ps -q wordpress) bash -c "chown -R www-data:www-data /var/www/html"
```

### Complete Reset
To start fresh:
```bash
docker-compose down -v
docker system prune -af --volumes
docker-compose up -d --build
```

### Image Loading Issues
If images aren't loading correctly:
1. Check WordPress Address (URL) and Site Address (URL) in Settings → General
2. Ensure they match the WP_HOME and WP_SITEURL values in docker-compose.yml
3. Clear browser cache and WordPress cache if using a caching plugin

### Database Connection Issues
1. Wait for MySQL container to be healthy (check with `docker-compose ps`)
2. Verify credentials in .env file match docker-compose.yml
3. Try using root credentials for phpMyAdmin if wp_user access fails

### Security Notes
- All database ports are bound to localhost only
- Environment variables are used for sensitive data
- Health checks ensure services are ready before dependencies start
- Resource limits prevent container resource exhaustion
