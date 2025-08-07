"""
Database helper functions with robust error handling for Farm Vision
Provides database operations with connection resilience and proper error recovery
"""
import logging
import time
from functools import wraps
from sqlalchemy.exc import OperationalError, DatabaseError, DisconnectionError
from sqlalchemy.orm.exc import DetachedInstanceError
from flask import current_app
from app import db

def retry_db_operation(max_retries=3, delay=1.0):
    """
    Decorator to retry database operations with exponential backoff
    Handles common database connection issues gracefully
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (OperationalError, DatabaseError, DisconnectionError) as e:
                    last_exception = e
                    error_msg = str(e).lower()
                    
                    # Log the specific error
                    logging.warning(f"Database operation failed (attempt {attempt + 1}/{max_retries}): {e}")
                    
                    # Check if it's a connection issue we can retry
                    if any(keyword in error_msg for keyword in [
                        'connection', 'timeout', 'eof detected', 'ssl', 'server closed',
                        'broken pipe', 'connection reset', 'network'
                    ]):
                        if attempt < max_retries - 1:
                            wait_time = delay * (2 ** attempt)  # Exponential backoff
                            logging.info(f"Retrying database operation in {wait_time} seconds...")
                            time.sleep(wait_time)
                            
                            # Try to recover the database session
                            try:
                                db.session.rollback()
                                db.session.close()
                            except Exception as session_error:
                                logging.debug(f"Session cleanup error (expected): {session_error}")
                            continue
                    else:
                        # Non-retryable error
                        break
                except DetachedInstanceError as e:
                    # Handle detached instance errors
                    logging.warning(f"Detached instance error: {e}")
                    try:
                        db.session.merge()
                        return func(*args, **kwargs)
                    except Exception:
                        last_exception = e
                        break
                except Exception as e:
                    # Non-database errors should not be retried
                    last_exception = e
                    break
            
            # All retries failed
            logging.error(f"Database operation failed after {max_retries} attempts: {last_exception}")
            raise last_exception
            
        return wrapper
    return decorator

@retry_db_operation(max_retries=2)
def safe_count_query(query, error_default=0):
    """
    Safely execute a count query with error handling
    Returns error_default value if query fails
    """
    try:
        return query.count()
    except Exception as e:
        logging.error(f"Count query failed: {e}")
        return error_default

@retry_db_operation(max_retries=2) 
def safe_scalar_query(query, error_default=None):
    """
    Safely execute a scalar query with error handling
    Returns error_default value if query fails
    """
    try:
        return query.scalar()
    except Exception as e:
        logging.error(f"Scalar query failed: {e}")
        return error_default

@retry_db_operation(max_retries=2)
def safe_all_query(query, error_default=None):
    """
    Safely execute a query.all() with error handling
    Returns error_default value (empty list) if query fails
    """
    try:
        return query.all()
    except Exception as e:
        logging.error(f"Query.all() failed: {e}")
        return error_default or []

@retry_db_operation(max_retries=2)
def safe_first_query(query, error_default=None):
    """
    Safely execute a query.first() with error handling
    Returns error_default value if query fails
    """
    try:
        return query.first()
    except Exception as e:
        logging.error(f"Query.first() failed: {e}")
        return error_default

def handle_db_connection_error(error):
    """
    Handle database connection errors and provide user-friendly messages
    """
    error_msg = str(error).lower()
    
    if 'ssl' in error_msg or 'eof detected' in error_msg:
        return "Database connection interrupted. Please refresh the page and try again."
    elif 'timeout' in error_msg:
        return "Database operation timed out. Please try again in a moment."
    elif 'connection' in error_msg:
        return "Database connection error. Please check your network and try again."
    else:
        return "Database error occurred. Please try again or contact support if the issue persists."

def ensure_db_connection():
    """
    Ensure database connection is alive, reconnect if necessary
    """
    try:
        # Simple connectivity test
        db.session.execute('SELECT 1')
        db.session.commit()
        return True
    except Exception as e:
        logging.warning(f"Database connectivity test failed: {e}")
        try:
            db.session.rollback()
            db.session.close()
        except Exception:
            pass
        return False