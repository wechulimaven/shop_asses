
run_tests:
	docker-compose -f docker-compose.yml -f docker-compose.stage.yml build
	docker-compose -f docker-compose.yml -f docker-compose.stage.yml exec web python3 manage.py test

build_local:
	docker-compose build

run_local:
	docker-compose up --build -d
	docker-compose logs -f web

run_local_test:
	docker-compose exec web python3 manage.py test

run_command:
	docker-compose exec web python manage.py create_super_user

run_shell:
	docker-compose exec web python manage.py shell

run_migrations:
	docker-compose exec web python manage.py makemigrations
	docker-compose exec web python manage.py migrate

merge_migrations:
	docker-compose exec web python manage.py migrate --merge

build_image_staging:
	docker-compose -f docker-compose.yml -f docker-compose.stage.yml build

push_image_staging:
	docker-compose -f docker-compose.yml -f docker-compose.stage.yml push

run_staging:
	docker-compose -f docker-compose.yml -f docker-compose.stage.yml up -d --build
	docker-compose -f docker-compose.yml -f docker-compose.stage.yml logs -f web

run_command_testing:
	docker-compose -f docker-compose.yml -f docker-compose.stage.yml exec web python3 manage.py create_super_user
