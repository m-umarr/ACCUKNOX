FROM python:3.9-slim


COPY . ./app
WORKDIR /app


RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt



COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=SocialApp.settings

ENTRYPOINT ["/entrypoint.sh"]
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]