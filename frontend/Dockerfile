########## STAGE 1 ##########
# First stage: build the React application
FROM node:22.16.0-alpine AS builder

# Set the maintainer label
LABEL author="LokaSync team"
LABEL description="LokaSync frontend service"
LABEL version="1.0.5"

# Set environment variables
ENV APP_DIR="/lokasync"
ENV APP_PORT="3000"
ENV LOCAL_USER="lokasync-frontend"
ENV LOCAL_GROUP="lokasync-group"

# Create a non-root user and group
RUN addgroup -S $LOCAL_GROUP && \
  adduser -S $LOCAL_USER -G $LOCAL_GROUP

# Create the application directory
RUN mkdir -p $APP_DIR && \
  chown $LOCAL_USER:$LOCAL_GROUP $APP_DIR && \
  chmod 755 $APP_DIR

# Set the working directory
WORKDIR $APP_DIR

# Copy the package-lock.json and install dependencies
COPY package.json ./
RUN npm i --silent

# Copy the application code
COPY ./ ./

# Build the application for production
RUN npm i -g npm@latest typescript && npm run build:prod

# Verify the build output (dist folder)
RUN ls -lah $APP_DIR/dist && \
  echo "Build completed."

# Copy the built files to a specific directory
RUN mkdir -p /dist && \
  chown $LOCAL_USER:$LOCAL_GROUP /dist && \
  chmod 755 /dist && \
  cp -r $APP_DIR/dist/* /dist/

########## STAGE 2 ##########
# Final stage: use Nginx to serve the React built application
FROM nginx:stable-alpine

# Remove default Nginx static web files
RUN rm -rf /usr/share/nginx/html/*

# Copy custom configuration file, but backup the default configuration first
RUN mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.default
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf

# Copy the built files to the Nginx HTML directory
COPY --from=builder /dist /usr/share/nginx/html/

# Expose the Nginx port
EXPOSE 3000

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]