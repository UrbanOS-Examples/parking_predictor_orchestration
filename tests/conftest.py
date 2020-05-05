import pytest
import time
import logging

pytest_plugins = ["docker_compose"]


@pytest.fixture(autouse=False, scope='session')
def wait_for_sql_server(session_scoped_container_getter):
  for _ in range(50):
    service = session_scoped_container_getter.get("sql_server")
    logging.debug(f"Waiting for {service} to be healthy")
    if service.get('State.Health.Status') == 'healthy':
      return
    
    time.sleep(1)

  raise Exception('Timed out waiting for services to be healthy')