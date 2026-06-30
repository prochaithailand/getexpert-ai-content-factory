import time
import logging

def retry(max_retries=3, delays=[2, 5, 10], exceptions=(Exception,)):
    """
    Decorator สำหรับทำ Retry Logic เมื่อเรียกใช้งานฟังก์ชันล้มเหลว
    นับรอบตั้งแต่ 1 ถึง max_retries และดีเลย์ตามลำดับเวลาที่กำหนด
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = delays[attempt] if attempt < len(delays) else delays[-1]
                        logging.warning(
                            f"ฟังก์ชัน '{func.__name__}' เกิดความผิดพลาดชั่วคราว: {e}. "
                            f"กำลังพยายามใหม่รอบที่ {attempt + 1}/{max_retries} ในอีก {delay} วินาที..."
                        )
                        time.sleep(delay)
                    else:
                        logging.error(f"ฟังก์ชัน '{func.__name__}' ล้มเหลวครบจำนวนการ Retry {max_retries} รอบแล้ว")
            raise last_exception
        return wrapper
    return decorator
