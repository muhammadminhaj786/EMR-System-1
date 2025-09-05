import os
import shutil
import logging
from flask import current_app
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

class FileService:
    """Service for handling file operations"""
    
    @staticmethod
    def save_upload(file, filename):
        """Save uploaded file to uploads directory"""
        try:
            filename = secure_filename(filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            file_path = os.path.join(upload_folder, filename)
            
            # Handle duplicate filenames
            counter = 1
            base_name, ext = os.path.splitext(filename)
            while os.path.exists(file_path):
                new_filename = f"{base_name}_{counter}{ext}"
                file_path = os.path.join(upload_folder, new_filename)
                filename = new_filename
                counter += 1
            
            file.save(file_path)
            logger.info(f"File saved: {file_path}")
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            raise
    
    @staticmethod
    def move_to_signed(original_path, consent_id):
        """Move file from uploads to signed directory"""
        try:
            if not os.path.exists(original_path):
                raise FileNotFoundError(f"Original file not found: {original_path}")
            
            signed_folder = current_app.config['SIGNED_FOLDER']
            filename = os.path.basename(original_path)
            base_name, ext = os.path.splitext(filename)
            signed_filename = f"{base_name}_signed_{consent_id}{ext}"
            signed_path = os.path.join(signed_folder, signed_filename)
            
            # Copy file to signed directory
            shutil.copy2(original_path, signed_path)
            logger.info(f"File copied to signed directory: {signed_path}")
            
            return signed_path
            
        except Exception as e:
            logger.error(f"Error moving file to signed: {str(e)}")
            raise
    
    @staticmethod
    def delete_file(file_path):
        """Delete a file safely"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"File deleted: {file_path}")
            else:
                logger.warning(f"File not found for deletion: {file_path}")
                
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            raise
