#!/bin/sh

read -p 'Enter DRAGRACE Database Host - Hit Enter for defualt (localhost): ' db_host
db_host=${db_host:-localhost}
export DRAGRACE_DATABASE_HOST="$db_host"
echo DRAGRACE_DATABASE_HOST set to $db_host

read -p 'Enter DRAGRACE Database Port - Hit Enter for default (5432): ' db_port
db_port=${db_port:-5432}
export DRAGRACE_DATABASE_PORT="$db_port"
echo DRAGRACE_DATABASE_PORT set to $db_port

read -p 'Enter DRAGRACE Database Name - Hit Enter for default (dragrace): ' db_name
db_name=${db_name:-dragrace}
export DRAGRACE_DATABASE_NAME="$db_name"
echo DRAGRACE_DATABASE_NAME set to $db_name

read -p 'Enter DRAGRACE Database Admin User - Hit Enter for default (postgres) : ' db_user
db_user=${db_user:-postgres}
export DRAGRACE_DATABASE_ADMIN="$db_user"
echo DRAGRACE_DATABASE_ADMIN set to $db_user

read -p 'Enter DRAGRACE Frontend URL - Hit Enter for default (http://localhost:3000) : ' frontend_url
frontend_url=${frontend_url:-http://localhost:3000}
export DRAGRACE_FRONTEND_URL="$frontend_url"
echo DRAGRACE_FRONTEND_URL set to $frontend_url

read -s -p 'Enter DRAGRACE Database Admin Password: ' db_pass
export DRAGRACE_DATABASE_PASSWORD="$db_pass"
echo DRAGRACE_DATABASE_PASSWORD set

read -p 'Enter Email host user: ' email_host_user
export EMAIL_HOST_USER=$email_host_user
echo EMAIL_HOST_USER set to $email_host_user

read -s -p 'Enter email host password: ' email_host_password
export EMAIL_HOST_PASSWORD="$email_host_password"
echo EMAIL_HOST_PASSWORD set
