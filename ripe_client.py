# https://data.ris.ripe.net/rrcXX/YYYY.MM/TYPE.YYYYMMDD.HHmm.gz

# with:

# XX = the RRC number
# YYYY = year
# MM = month
# TYPE = the type of file, which is either bview (dumps) or update (updates)
# DD = day
# HH = hour
# mm = minute
# Currently dumps are created every 8 hours, and updates are created every 5 minutes
#


import tempfile
import os
import requests
from pathlib import Path

class RIPEClient:
    def __init__(self,
                 cacheLocation=False,
                 baseURL='https://data.ris.ripe.net',
                 logging=False):
        
        self.baseURL = baseURL
        self.logging = logging

        # Mapping possible cache location passed
        if (cacheLocation):
            self.workdir = cacheLocation
        else:
            self.workdir = tempfile.gettempdir() + "/ripe"

        # Creating the directory if not exists
        if not os.path.exists(self.workdir):
            self.log_info("Creating the directory: " + self.workdir)
            os.makedirs(self.workdir)

    def log_info(self, msg):
        if self.logging:
            return self.logging.info(msg)
        else: print(msg)
    
    def log_error(self, msg):
        if self.logging:
            return self.logging.error(msg)
        else: print(msg)
        
    def log_warning(self, msg):
        if self.logging:
            return self.logging.warning(msg)
        
    def create_path_if_not_exists(self,path):
        try:
            if not os.path.exists(path):
                self.log_info('Creating dir: ' + path)
                path = Path(path)
                path.mkdir(parents=True, exist_ok=True)
            return True
        except:
            self.log_error('Failure when creating the dir: ' + path)
            return False
            
        
    def generate_update_url(self, year, month, day, hour, minute, rrc=4):
        
        return "{baseURL}/rrc{rrc}/{year}.{month}/updates.{year}{month}{day}.{hour}{minute}.gz".format(
            baseURL=self.baseURL,
            year=year,
            month="{:02d}".format(month),
            day="{:02d}".format(day),
            hour="{:02d}".format(hour),
            minute="{:02d}".format(minute),
            rrc="{:02d}".format(rrc)
        )
    
    def generate_update_local_path(self, year, month, day, hour, minute, rrc=4):

        return "{workdir}/rrc{rrc}/{year}.{month}/updates.{year}{month}{day}.{hour}{minute}.gz".format(
            workdir=self.workdir,
            year=year,
            month="{:02d}".format(month),
            day="{:02d}".format(day),
            hour="{:02d}".format(hour),
            minute="{:02d}".format(minute),
            rrc="{:02d}".format(rrc)
        )
        
        
    def download_update_file(self, year, month, day, hour, minute, rrc=4):
        
        # Setting the local attributes
        filePath = self.generate_update_local_path(year, month, day, hour, minute, rrc)
        head, tail = os.path.split(filePath)
        self.create_path_if_not_exists(head)

        # Setting the URL
        url = self.generate_update_url(year, month, day, hour, minute, rrc)

        # Checking if the file was already downloaded before
        if not os.path.exists(filePath):
        
            # Downloading the file
            self.log_info('Downloading RIPE file: ' + url)
            try:
                res = requests.get(url, allow_redirects=True)
                # Saving the file
                try:
                    open(filePath, 'wb').write(res.content)
                    self.log_info('File saved in: ' + url)
                    if os.path.exists(filePath):
                        return filePath
                    else:
                        raise Exception('Downloaded file not found in: ' + url)
                except:
                    raise Exception('Failure when downloading the file: ' + url)
            except:
                raise Exception('Failure when downloading the file: ' + url)
            
        else:
            self.log_info('Download prevented because the file was found in cache: ' + url)
            return filePath
        
    #def download_updates_interval_files(self, yearStart, monthStart, dayStart, hourStart, minuteStart, yearEnd, monthEnd, dayEnd, hourEnd, minuteEnd, rrc=4):

            
        
