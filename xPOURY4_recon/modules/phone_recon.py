"""
Phone reconnaissance module for xPOURY4 Recon
Author: xPOURY4
"""

import re
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from typing import Dict, Any
from .base_module import BaseReconModule
from ..core.config_manager import config
from ..core.logger import logger
from ..core.exceptions import ValidationException


class PhoneRecon(BaseReconModule):
    """Enhanced phone reconnaissance module"""
    
    def __init__(self):
        super().__init__("phone_recon")
        self.include_carrier = config.get("modules.phone_recon.include_carrier", True)
        self.include_location = config.get("modules.phone_recon.include_location", True)
    
    def is_configured(self) -> bool:
        """Check if module is properly configured"""
        return True  # No API keys required for basic phone lookup
    
    def _validate_phone(self, phone_number: str) -> bool:
        """Validate phone number format"""
        try:
            parsed = phonenumbers.parse(phone_number, None)
            return phonenumbers.is_valid_number(parsed)
        except:
            return False
    
    async def investigate(self, phone_number: str, **kwargs) -> Dict[str, Any]:
        """Investigate phone number"""
        try:
            if not self.validate_input(phone_number, self._validate_phone):
                raise ValidationException(f"Invalid phone number format: {phone_number}")
            
            # Parse the phone number
            parsed_number = phonenumbers.parse(phone_number, None)
            
            # Get basic information
            phone_data = {
                'original_number': phone_number,
                'formatted_national': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.NATIONAL),
                'formatted_international': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                'formatted_e164': phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164),
                'country_code': parsed_number.country_code,
                'national_number': parsed_number.national_number,
                'is_valid': phonenumbers.is_valid_number(parsed_number),
                'is_possible': phonenumbers.is_possible_number(parsed_number),
                'number_type': self._get_number_type(parsed_number)
            }
            
            # Get location information
            if self.include_location:
                phone_data['location'] = self._get_location_info(parsed_number)
            
            # Get carrier information
            if self.include_carrier:
                phone_data['carrier'] = self._get_carrier_info(parsed_number)
            
            # Get timezone information
            phone_data['timezones'] = self._get_timezone_info(parsed_number)
            
            return self.format_result(True, phone_data)
            
        except Exception as e:
            logger.error(f"Phone reconnaissance failed for {phone_number}: {e}")
            return self.format_result(False, error=str(e))
    
    def _get_number_type(self, parsed_number) -> str:
        """Get the type of phone number"""
        number_type = phonenumbers.number_type(parsed_number)
        type_mapping = {
            phonenumbers.PhoneNumberType.FIXED_LINE: "Fixed Line",
            phonenumbers.PhoneNumberType.MOBILE: "Mobile",
            phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "Fixed Line or Mobile",
            phonenumbers.PhoneNumberType.TOLL_FREE: "Toll Free",
            phonenumbers.PhoneNumberType.PREMIUM_RATE: "Premium Rate",
            phonenumbers.PhoneNumberType.SHARED_COST: "Shared Cost",
            phonenumbers.PhoneNumberType.VOIP: "VoIP",
            phonenumbers.PhoneNumberType.PERSONAL_NUMBER: "Personal Number",
            phonenumbers.PhoneNumberType.PAGER: "Pager",
            phonenumbers.PhoneNumberType.UAN: "Universal Access Number",
            phonenumbers.PhoneNumberType.VOICEMAIL: "Voicemail",
            phonenumbers.PhoneNumberType.UNKNOWN: "Unknown"
        }
        return type_mapping.get(number_type, "Unknown")
    
    def _get_location_info(self, parsed_number) -> Dict[str, str]:
        """Get location information"""
        try:
            return {
                'country': geocoder.description_for_number(parsed_number, "en"),
                'region': geocoder.description_for_number(parsed_number, "en")
            }
        except Exception as e:
            logger.warning(f"Failed to get location info: {e}")
            return {'error': str(e)}
    
    def _get_carrier_info(self, parsed_number) -> Dict[str, str]:
        """Get carrier information"""
        try:
            carrier_name = carrier.name_for_number(parsed_number, "en")
            return {
                'name': carrier_name if carrier_name else "Unknown",
                'safe_display': carrier.safe_display_name(parsed_number, "en")
            }
        except Exception as e:
            logger.warning(f"Failed to get carrier info: {e}")
            return {'error': str(e)}
    
    def _get_timezone_info(self, parsed_number) -> list:
        """Get timezone information"""
        try:
            timezones = timezone.time_zones_for_number(parsed_number)
            return list(timezones) if timezones else []
        except Exception as e:
            logger.warning(f"Failed to get timezone info: {e}")
            return [] 