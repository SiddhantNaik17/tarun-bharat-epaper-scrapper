from epaper_scrapper.driver import Driver


driver = Driver()
driver.download_latest_epaper()
driver.quit()
