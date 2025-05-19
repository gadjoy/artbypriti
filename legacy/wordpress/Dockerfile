FROM wordpress:6.4

# Set PHP configurations
RUN echo "upload_max_filesize=512M" > /usr/local/etc/php/conf.d/custom.ini \
    && echo "post_max_size=512M" >> /usr/local/etc/php/conf.d/custom.ini \
    && echo "memory_limit=512M" >> /usr/local/etc/php/conf.d/custom.ini \
    && echo "max_execution_time=300" >> /usr/local/etc/php/conf.d/custom.ini \
    && echo "max_input_time=300" >> /usr/local/etc/php/conf.d/custom.ini 