"""
Enhanced Email Analysis Module for PhishGuard
Real-time phishing detection for email with comprehensive error handling
"""

import re
import base64
import email
from email import policy
from email.parser import Parser, BytesParser
from email.message import EmailMessage
from urllib.parse import urlparse
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple
import traceback
from datetime import datetime
import dns.resolver
import socket

# Import our URL checking functionality
from .external_apis import check_url_with_external_apis
from .feature import featureExtraction


class EnhancedEmailHeaderAnalyzer:
    """Enhanced email header analysis with real-time validation"""
    
    def __init__(self):
        self.suspicious_indicators = []
        self.authentication_results = {}
        self.routing_info = []
        self.parsed_headers = {}
        self.errors = []
    
    def analyze(self, headers_text: str) -> Dict[str, Any]:
        """
        Comprehensive email header analysis with error handling
        
        Args:
            headers_text: Raw email headers as text
            
        Returns:
            dict: Analysis results with risk assessment and errors
        """
        self.suspicious_indicators = []
        self.authentication_results = {}
        self.routing_info = []
        self.errors = []
        
        try:
            # Validate input
            if not headers_text or not isinstance(headers_text, str):
                self.errors.append({
                    'type': 'validation',
                    'message': 'Invalid or empty headers provided',
                    'severity': 'critical'
                })
                return self._error_response('Invalid headers input')
            
            # Parse the headers
            try:
                headers = Parser(policy=policy.default).parsestr(headers_text)
            except Exception as e:
                self.errors.append({
                    'type': 'parsing',
                    'message': f'Failed to parse email headers: {str(e)}',
                    'severity': 'critical'
                })
                return self._error_response(f'Header parsing failed: {str(e)}')
            
            # Extract key headers with validation
            self.parsed_headers = self._extract_headers(headers)
            
            # Check for authentication results
            self._parse_authentication_results()
            
            # Check for spoofing indicators
            self._check_spoofing_indicators()
            
            # Check unusual routing
            self._check_unusual_routing()
            
            # Check for reply-to mismatches
            self._check_reply_to_mismatch()
            
            # Check received headers timing
            self._check_suspicious_timing()
            
            # Validate sender domain
            self._validate_sender_domain()
            
            # Check for forged headers
            self._check_forged_headers()
            
            # Calculate risk score
            risk_score = self._calculate_risk_score()
            
            return {
                'status': 'success',
                'parsed_headers': self.parsed_headers,
                'authentication_results': self.authentication_results,
                'suspicious_indicators': self.suspicious_indicators,
                'routing_info': self.routing_info,
                'errors': self.errors,
                'risk_score': risk_score,
                'risk_level': self._risk_level_from_score(risk_score),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.errors.append({
                'type': 'exception',
                'message': f'Unexpected error in header analysis: {str(e)}',
                'severity': 'critical',
                'traceback': traceback.format_exc()
            })
            return self._error_response(f'Analysis failed: {str(e)}')
    
    def _extract_headers(self, headers: EmailMessage) -> Dict[str, Any]:
        """Safely extract headers with validation"""
        try:
            return {
                'from': self._safe_get_header(headers, 'From'),
                'to': self._safe_get_header(headers, 'To'),
                'subject': self._safe_get_header(headers, 'Subject'),
                'date': self._safe_get_header(headers, 'Date'),
                'message_id': self._safe_get_header(headers, 'Message-ID'),
                'reply_to': self._safe_get_header(headers, 'Reply-To'),
                'return_path': self._safe_get_header(headers, 'Return-Path'),
                'received': self._parse_received_headers(headers),
                'authentication_results': self._safe_get_header(headers, 'Authentication-Results'),
                'dkim_signature': self._safe_get_header(headers, 'DKIM-Signature'),
                'received_spf': self._safe_get_header(headers, 'Received-SPF'),
                'x_mailer': self._safe_get_header(headers, 'X-Mailer'),
                'x_originating_ip': self._safe_get_header(headers, 'X-Originating-IP'),
                'spf': '',
                'dkim': '',
                'dmarc': ''
            }
        except Exception as e:
            self.errors.append({
                'type': 'extraction',
                'message': f'Error extracting headers: {str(e)}',
                'severity': 'medium'
            })
            return {}
    
    def _safe_get_header(self, headers: EmailMessage, header_name: str) -> str:
        """Safely get a header value"""
        try:
            value = headers.get(header_name, '')
            return str(value) if value else ''
        except:
            return ''
    
    def _parse_received_headers(self, headers: EmailMessage) -> List[str]:
        """Extract and parse Received headers"""
        try:
            received_headers = headers.get_all('Received', [])
            return [str(h) for h in received_headers] if received_headers else []
        except Exception as e:
            self.errors.append({
                'type': 'parsing',
                'message': f'Error parsing Received headers: {str(e)}',
                'severity': 'low'
            })
            return []
    
    def _parse_authentication_results(self):
        """Parse SPF, DKIM, and DMARC results from headers"""
        try:
            auth_results = self.parsed_headers.get('authentication_results', '')
            received_spf = self.parsed_headers.get('received_spf', '')
            
            # Parse SPF
            spf_match = re.search(r'spf=(\w+)', auth_results, re.IGNORECASE)
            if not spf_match and received_spf:
                spf_match = re.search(r'(pass|fail|softfail|neutral|none)', received_spf, re.IGNORECASE)
            
            if spf_match:
                spf_result = spf_match.group(1).lower()
                self.authentication_results['spf'] = spf_result
                self.parsed_headers['spf'] = spf_result
            
            # Parse DKIM
            dkim_match = re.search(r'dkim=(\w+)', auth_results, re.IGNORECASE)
            if dkim_match:
                dkim_result = dkim_match.group(1).lower()
                self.authentication_results['dkim'] = dkim_result
                self.parsed_headers['dkim'] = dkim_result
            
            # Parse DMARC
            dmarc_match = re.search(r'dmarc=(\w+)', auth_results, re.IGNORECASE)
            if dmarc_match:
                dmarc_result = dmarc_match.group(1).lower()
                self.authentication_results['dmarc'] = dmarc_result
                self.parsed_headers['dmarc'] = dmarc_result
                
        except Exception as e:
            self.errors.append({
                'type': 'parsing',
                'message': f'Error parsing authentication results: {str(e)}',
                'severity': 'medium'
            })
    
    def _check_spoofing_indicators(self):
        """Check for email spoofing indicators"""
        try:
            # Check SPF
            if 'spf' in self.authentication_results:
                spf_result = self.authentication_results['spf']
                if spf_result == 'fail':
                    self.suspicious_indicators.append({
                        'type': 'authentication',
                        'name': 'SPF Authentication Failed',
                        'description': 'Email failed SPF check - sender may be forged',
                        'severity': 'critical'
                    })
                elif spf_result == 'softfail':
                    self.suspicious_indicators.append({
                        'type': 'authentication',
                        'name': 'SPF Soft Fail',
                        'description': 'Email SPF check returned soft fail',
                        'severity': 'high'
                    })
                elif spf_result == 'none':
                    self.suspicious_indicators.append({
                        'type': 'authentication',
                        'name': 'No SPF Record',
                        'description': 'Sender domain has no SPF record',
                        'severity': 'medium'
                    })
            else:
                self.suspicious_indicators.append({
                    'type': 'authentication',
                    'name': 'Missing SPF Authentication',
                    'description': 'No SPF authentication results found',
                    'severity': 'medium'
                })
            
            # Check DKIM
            if 'dkim' in self.authentication_results:
                if self.authentication_results['dkim'] != 'pass':
                    self.suspicious_indicators.append({
                        'type': 'authentication',
                        'name': 'DKIM Authentication Failed',
                        'description': 'Email failed DKIM signature validation',
                        'severity': 'critical'
                    })
            else:
                self.suspicious_indicators.append({
                    'type': 'authentication',
                    'name': 'Missing DKIM Signature',
                    'description': 'No DKIM signature present',
                    'severity': 'medium'
                    })
            
            # Check DMARC
            if 'dmarc' in self.authentication_results:
                if self.authentication_results['dmarc'] != 'pass':
                    self.suspicious_indicators.append({
                        'type': 'authentication',
                        'name': 'DMARC Policy Failure',
                        'description': 'Email failed DMARC policy check',
                        'severity': 'high'
                    })
                    
        except Exception as e:
            self.errors.append({
                'type': 'analysis',
                'message': f'Error checking spoofing indicators: {str(e)}',
                'severity': 'low'
            })
    
    def _check_unusual_routing(self):
        """Check for unusual email routing patterns"""
        try:
            received_headers = self.parsed_headers.get('received', [])
            
            if not received_headers:
                self.suspicious_indicators.append({
                    'type': 'routing',
                    'name': 'Missing Received Headers',
                    'description': 'No routing information present',
                    'severity': 'high'
                })
                return
            
            # Extract IP addresses and countries
            ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
            countries = set()
            
            for i, header in enumerate(received_headers):
                ips = re.findall(ip_pattern, header)
                
                if ips:
                    self.routing_info.append({
                        'hop': i + 1,
                        'header': header[:200] + '...' if len(header) > 200 else header,
                        'ip_addresses': ips
                    })
            
            # Check for excessive hops
            if len(received_headers) > 15:
                self.suspicious_indicators.append({
                    'type': 'routing',
                    'name': 'Excessive Mail Hops',
                    'description': f'Email passed through {len(received_headers)} servers',
                    'severity': 'medium'
                })
            
            # Check for very few hops (less than 2 is suspicious)
            if len(received_headers) < 2:
                self.suspicious_indicators.append({
                    'type': 'routing',
                    'name': 'Insufficient Routing Information',
                    'description': 'Email has unusually few routing hops',
                    'severity': 'high'
                })
                
        except Exception as e:
            self.errors.append({
                'type': 'analysis',
                'message': f'Error checking routing: {str(e)}',
                'severity': 'low'
            })
    
    def _check_reply_to_mismatch(self):
        """Check for From/Reply-To mismatches"""
        try:
            from_email = self._extract_email(self.parsed_headers.get('from', ''))
            reply_to = self._extract_email(self.parsed_headers.get('reply_to', ''))
            return_path = self._extract_email(self.parsed_headers.get('return_path', ''))
            
            if reply_to and from_email and reply_to != from_email:
                # Check if it's the same domain
                from_domain = from_email.split('@')[1] if '@' in from_email else ''
                reply_domain = reply_to.split('@')[1] if '@' in reply_to else ''
                
                if from_domain != reply_domain:
                    self.suspicious_indicators.append({
                        'type': 'mismatch',
                        'name': 'Reply-To Domain Mismatch',
                        'description': f'Reply-To ({reply_to}) uses different domain than From ({from_email})',
                        'severity': 'critical'
                    })
            
            if return_path and from_email and return_path != from_email:
                from_domain = from_email.split('@')[1] if '@' in from_email else ''
                return_domain = return_path.split('@')[1] if '@' in return_path else ''
                
                if from_domain != return_domain:
                    self.suspicious_indicators.append({
                        'type': 'mismatch',
                        'name': 'Return-Path Domain Mismatch',
                        'description': f'Return-Path ({return_path}) uses different domain',
                        'severity': 'high'
                    })
                    
        except Exception as e:
            self.errors.append({
                'type': 'analysis',
                'message': f'Error checking reply-to mismatch: {str(e)}',
                'severity': 'low'
            })
    
    def _check_suspicious_timing(self):
        """Check for suspicious timing in received headers"""
        try:
            received_headers = self.parsed_headers.get('received', [])
            
            # Look for time inconsistencies
            time_pattern = r'(\d{1,2}\s+\w{3}\s+\d{4}\s+\d{1,2}:\d{2}:\d{2})'
            
            times = []
            for header in received_headers:
                time_matches = re.findall(time_pattern, header)
                times.extend(time_matches)
            
            # If we have timestamps, check for future dates
            if times:
                for time_str in times:
                    try:
                        # Basic check - emails shouldn't have future timestamps
                        pass  # Would need proper date parsing
                    except:
                        pass
                        
        except Exception as e:
            self.errors.append({
                'type': 'analysis',
                'message': f'Error checking timing: {str(e)}',
                'severity': 'low'
            })
    
    def _validate_sender_domain(self):
        """Validate sender domain with DNS lookup"""
        try:
            from_email = self._extract_email(self.parsed_headers.get('from', ''))
            if not from_email or '@' not in from_email:
                return
            
            domain = from_email.split('@')[1]
            
            # Check if domain has MX records
            try:
                mx_records = dns.resolver.resolve(domain, 'MX')
                if not mx_records:
                    self.suspicious_indicators.append({
                        'type': 'domain',
                        'name': 'No MX Records',
                        'description': f'Sender domain {domain} has no mail exchange records',
                        'severity': 'high'
                    })
            except dns.resolver.NXDOMAIN:
                self.suspicious_indicators.append({
                    'type': 'domain',
                    'name': 'Invalid Domain',
                    'description': f'Sender domain {domain} does not exist',
                    'severity': 'critical'
                })
            except dns.resolver.NoAnswer:
                self.suspicious_indicators.append({
                    'type': 'domain',
                    'name': 'No MX Records',
                    'description': f'Sender domain {domain} has no mail exchange records',
                    'severity': 'high'
                })
            except Exception:
                # DNS lookup failed, but this might be network issue
                pass
                
        except Exception as e:
            self.errors.append({
                'type': 'validation',
                'message': f'Error validating sender domain: {str(e)}',
                'severity': 'low'
            })
    
    def _check_forged_headers(self):
        """Check for signs of forged or manipulated headers"""
        try:
            # Check for missing Message-ID
            message_id = self.parsed_headers.get('message_id', '')
            if not message_id:
                self.suspicious_indicators.append({
                    'type': 'headers',
                    'name': 'Missing Message-ID',
                    'description': 'Email lacks Message-ID header',
                    'severity': 'medium'
                })
            
            # Check for suspicious X-Mailer or User-Agent
            x_mailer = self.parsed_headers.get('x_mailer', '').lower()
            suspicious_mailers = ['php', 'python', 'perl', 'script', 'bot']
            
            if any(mailer in x_mailer for mailer in suspicious_mailers):
                self.suspicious_indicators.append({
                    'type': 'headers',
                    'name': 'Suspicious Mail Client',
                    'description': f'Email sent using suspicious client: {x_mailer}',
                    'severity': 'medium'
                })
                
        except Exception as e:
            self.errors.append({
                'type': 'analysis',
                'message': f'Error checking forged headers: {str(e)}',
                'severity': 'low'
            })
    
    def _extract_email(self, header_value: str) -> str:
        """Extract email address from header value"""
        if not header_value:
            return ''
        
        try:
            email_pattern = r'[\w\.-]+@[\w\.-]+'
            match = re.search(email_pattern, header_value)
            return match.group(0).lower() if match else header_value.lower()
        except:
            return header_value.lower()
    
    def _calculate_risk_score(self) -> int:
        """Calculate comprehensive risk score"""
        score = 0
        
        try:
            # Critical indicators
            critical_indicators = [i for i in self.suspicious_indicators if i['severity'] == 'critical']
            score += len(critical_indicators) * 30
            
            # High severity indicators
            high_indicators = [i for i in self.suspicious_indicators if i['severity'] == 'high']
            score += len(high_indicators) * 20
            
            # Medium severity indicators
            medium_indicators = [i for i in self.suspicious_indicators if i['severity'] == 'medium']
            score += len(medium_indicators) * 10
            
            # Low severity indicators
            low_indicators = [i for i in self.suspicious_indicators if i['severity'] == 'low']
            score += len(low_indicators) * 5
            
            # Cap at 100
            return min(score, 100)
        except:
            return 50  # Default moderate risk if calculation fails
    
    def _risk_level_from_score(self, score: int) -> str:
        """Convert score to risk level"""
        if score >= 75:
            return 'Critical Risk'
        elif score >= 50:
            return 'High Risk'
        elif score >= 25:
            return 'Medium Risk'
        elif score >= 10:
            return 'Low Risk'
        else:
            return 'Safe'
    
    def _error_response(self, message: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            'status': 'error',
            'message': message,
            'parsed_headers': self.parsed_headers,
            'suspicious_indicators': self.suspicious_indicators,
            'errors': self.errors,
            'risk_score': 100,  # Maximum risk for errors
            'risk_level': 'Unknown',
            'timestamp': datetime.now().isoformat()
        }


class EnhancedEmailContentAnalyzer:
    """Enhanced email content analysis with real-time URL checking"""
    
    def __init__(self):
        self.suspicious_indicators = []
        self.extracted_urls = []
        self.social_engineering_tactics = []
        self.errors = []
        self.url_analysis_results = []
    
    def analyze(self, sender: str, subject: str, body: str, attachments: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Comprehensive email content analysis with real-time URL checking
        
        Args:
            sender: Sender email address
            subject: Email subject line
            body: Email body content
            attachments: List of attachment info dicts (optional)
            
        Returns:
            dict: Analysis results with risk assessment
        """
        self.suspicious_indicators = []
        self.extracted_urls = []
        self.social_engineering_tactics = []
        self.errors = []
        self.url_analysis_results = []
        
        try:
            # Validate inputs
            if not isinstance(sender, str):
                sender = str(sender) if sender else ''
            if not isinstance(subject, str):
                subject = str(subject) if subject else ''
            if not isinstance(body, str):
                body = str(body) if body else ''
            
            # Analyze sender
            self._analyze_sender(sender)
            
            # Analyze subject
            self._analyze_subject(subject)
            
            # Analyze body
            self._analyze_body(body)
            
            # Extract and analyze URLs with REAL-TIME checking
            self._extract_and_check_urls(body)
            
            # Analyze attachments if provided
            if attachments:
                self._analyze_attachments(attachments)
            
            # Check for obfuscation techniques
            self._check_obfuscation(body)
            
            # Calculate risk score
            risk_score = self._calculate_risk_score()
            
            return {
                'status': 'success',
                'suspicious_indicators': self.suspicious_indicators,
                'extracted_urls': self.extracted_urls,
                'url_analysis_results': self.url_analysis_results,
                'social_engineering_tactics': list(set(self.social_engineering_tactics)),
                'errors': self.errors,
                'risk_score': risk_score,
                'risk_level': self._risk_level_from_score(risk_score),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.errors.append({
                'type': 'exception',
                'message': f'Unexpected error in content analysis: {str(e)}',
                'severity': 'critical',
                'traceback': traceback.format_exc()
            })
            return self._error_response(f'Analysis failed: {str(e)}')
    
    def _analyze_sender(self, sender: str):
        """Enhanced sender analysis"""
        if not sender:
            return
        
        try:
            # Check for suspicious TLDs
            suspicious_tlds = ['.tk', '.pw', '.cf', '.ga', '.gq', '.ml', '.buzz', '.xyz', '.top', '.club', '.link', '.online', '.site']
            for tld in suspicious_tlds:
                if sender.lower().endswith(tld):
                    self.suspicious_indicators.append({
                        'type': 'sender',
                        'name': 'Suspicious Domain TLD',
                        'description': f'Sender uses high-risk top-level domain: {tld}',
                        'severity': 'high'
                    })
                    break
            
            # Check for lookalike/typosquatting domains
            sender_parts = sender.split('@')
            if len(sender_parts) > 1:
                domain = sender_parts[1].lower()
                
                # Check for common brand impersonation
                brand_patterns = {
                    'paypal': ['paypa1', 'paypall', 'pay-pal', 'paypa', 'paylpal'],
                    'amazon': ['amaz0n', 'amazn', 'amzon', 'arnazon'],
                    'microsoft': ['microsft', 'micr0soft', 'micro-soft'],
                    'google': ['goggle', 'g00gle', 'gooogle', 'googie'],
                    'apple': ['appl', 'app1e', 'ap-ple', 'appie'],
                    'facebook': ['faceb00k', 'facbook', 'face-book'],
                    'netflix': ['netflex', 'netflx', 'net-flix'],
                    'bank': ['bnk', 'b4nk', 'bankk']
                }
                
                for brand, variants in brand_patterns.items():
                    for variant in variants:
                        if variant in domain and brand not in domain:
                            self.suspicious_indicators.append({
                                'type': 'sender',
                                'name': 'Brand Impersonation',
                                'description': f'Sender domain may impersonate {brand.upper()}',
                                'severity': 'critical'
                            })
                            self.social_engineering_tactics.append('impersonation')
                            break
                            
        except Exception as e:
            self.errors.append({
                'type': 'analysis',
                'message': f'Error analyzing sender: {str(e)}',
                'severity': 'low'
            })
    
    def _analyze_subject(self, subject: str):
        """Enhanced subject line analysis"""
        if not subject:
            return
        
        try:
            subject_lower = subject.lower()
            
            # Urgency indicators (expanded list)
            urgency_terms = [
                'urgent', 'immediate', 'attention required', 'important', 'alert',
                'action required', 'warning', 'critical', 'suspended', 'expires',
                'limited time', 'act now', 'hurry', 'last chance', 'final notice',
                'deadline', 'time sensitive'
            ]
            
            for term in urgency_terms:
                if term in subject_lower:
                    self.suspicious_indicators.append({
                        'type': 'subject',
                        'name': 'Urgency Tactic',
                        'description': f'Subject uses urgency: "{term}"',
                        'severity': 'medium'
                    })
                    self.social_engineering_tactics.append('urgency')
                    break
            
            # Financial/Account terms
            financial_terms = [
                'account', 'payment', 'invoice', 'transaction', 'bank', 'credit card',
                'paypal', 'deposit', 'withdraw', 'tax', 'refund', 'billing', 'verify',
                'confirm', 'update', 'suspended account', 'unusual activity'
            ]
            
            for term in financial_terms:
                if term in subject_lower:
                    self.suspicious_indicators.append({
                        'type': 'subject',
                        'name': 'Financial Target',
                        'description': f'Subject mentions: "{term}"',
                        'severity': 'medium'
                    })
                    break
            
            # Prize/Reward terms
            reward_terms = ['won', 'winner', 'prize', 'free', 'gift', 'reward', 'congratulations', 'selected']
            for term in reward_terms:
                if term in subject_lower:
                    self.social_engineering_tactics.append('reward')
                    break
            
            # Check for excessive punctuation
            if subject.count('!') > 2 or subject.count('?') > 2:
                self.suspicious_indicators.append({
                    'type': 'subject',
                    'name': 'Excessive Punctuation',
                    'description': 'Subject uses excessive punctuation marks',
                    'severity': 'low'
                })
            
            # Check for ALL CAPS
            if len(subject) > 10 and subject.isupper():
                self.suspicious_indicators.append({
                    'type': 'subject',
                    'name': 'All Caps Subject',
                    'description': 'Subject is entirely in capital letters',
                    'severity': 'low'
                })
                
        except Exception as e:
            self.errors.append({
                'type': 'analysis',
                'message': f'Error analyzing subject: {str(e)}',
                'severity': 'low'
            })
    
    def _analyze_body(self, body: str):
        """Enhanced body content analysis"""
        if not body:
            return
        
        try:
            body_lower = body.lower()
            
            # Phishing phrases (expanded)
            phishing_phrases = [
                'verify your account', 'confirm your account', 'update your information',
                'update your password', 'reset your password', 'suspicious activity',
                'unusual activity', 'click here to verify', 'security alert',
                'account suspended', 'account locked', 'unauthorized access',
                'confirm your identity', 'validate your account', 're-activate',
                'update payment method', 'billing problem'
            ]
            
            for phrase in phishing_phrases:
                if phrase in body_lower:
                    self.suspicious_indicators.append({
                        'type': 'body',
                        'name': 'Phishing Phrase',
                        'description': f'Contains: "{phrase}"',
                        'severity': 'high'
                    })
            
            # Social engineering tactics
            threat_phrases = [
                'account will be closed', 'legal action', 'permanent deletion',
                'criminal charges', 'lawsuit', 'terminate', 'expire',
                'lose access', 'permanently deleted'
            ]
            
            for phrase in threat_phrases:
                if phrase in body_lower:
                    self.social_engineering_tactics.append('threat')
                    self.suspicious_indicators.append({
                        'type': 'body',
                        'name': 'Threat Tactic',
                        'description': f'Uses threat: "{phrase}"',
                        'severity': 'high'
                    })
            
            # Check for poor grammar/spelling
            grammar_errors = [
                'kindely', 'securty', 'verifcation', 'informations', 'payed',
                'recieve', 'seperate', 'occured', 'neccesary'
            ]
            
            for error in grammar_errors:
                if error in body_lower:
                    self.suspicious_indicators.append({
                        'type': 'body',
                        'name': 'Spelling Errors',
                        'description': 'Email contains spelling/grammar errors',
                        'severity': 'medium'
                    })
                    break
            
            # Check for generic greetings
            generic_greetings = ['dear customer', 'dear user', 'dear member', 'valued customer']
            for greeting in generic_greetings:
                if greeting in body_lower:
                    self.suspicious_indicators.append({
                        'type': 'body',
                        'name': 'Generic Greeting',
                        'description': 'Uses generic greeting instead of personal name',
                        'severity': 'low'
                    })
                    break
                    
        except Exception as e:
            self.errors.append({
                'type': 'analysis',
                'message': f'Error analyzing body: {str(e)}',
                'severity': 'low'
            })
    
    def _extract_and_check_urls(self, body: str):
        """Extract URLs and check them in REAL-TIME against our detection APIs"""
        if not body:
            return
        
        try:
            # Enhanced URL extraction patterns
            url_patterns = [
                r'https?://[^\s<>"\']+',
                r'www\.[^\s<>"\']+',
                r'[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}(?:/[^\s<>"\']*)?'
            ]
            
            found_urls = []
            for pattern in url_patterns:
                urls = re.findall(pattern, body)
                found_urls.extend(urls)
            
            # Remove duplicates
            found_urls = list(set(found_urls))
            
            print(f"Found {len(found_urls)} URLs in email body")
            
            for url in found_urls[:10]:  # Limit to 10 URLs to avoid too many API calls
                url_info = self._check_single_url(url)
                self.extracted_urls.append(url_info)
                
        except Exception as e:
            self.errors.append({
                'type': 'extraction',
                'message': f'Error extracting URLs: {str(e)}',
                'severity': 'medium'
            })
    
    def _check_single_url(self, url: str) -> Dict[str, Any]:
        """Check a single URL with our API detection system"""
        url_info = {
            'url': url,
            'suspicious': False,
            'reason': '',
            'phishing_detection': None
        }
        
        try:
            # Normalize URL
            if not url.startswith(('http://', 'https://')):
                if url.startswith('www.'):
                    url = 'http://' + url
                else:
                    url = 'http://' + url
            
            url_info['url'] = url
            
            # Basic suspicious checks
            parsed = urlparse(url)
            
            # Check for IP address URLs
            if re.match(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', parsed.netloc):
                url_info['suspicious'] = True
                url_info['reason'] = 'Uses IP address instead of domain'
                
                self.suspicious_indicators.append({
                    'type': 'url',
                    'name': 'IP Address URL',
                    'description': f'Email contains IP-based URL: {url}',
                    'severity': 'critical'
                })
            
            # Check for @ symbol (redirection)
            if '@' in parsed.netloc:
                url_info['suspicious'] = True
                url_info['reason'] = 'Contains @ symbol (redirection trick)'
                
                self.suspicious_indicators.append({
                    'type': 'url',
                    'name': 'URL Redirection Trick',
                    'description': f'URL uses @ symbol: {url}',
                    'severity': 'critical'
                })
            
            # REAL-TIME CHECK: Use our API detection system
            print(f"Checking URL with APIs: {url}")
            try:
                api_result = check_url_with_external_apis(url)
                
                if api_result and api_result.get('status') != 'error':
                    is_phishing = api_result.get('is_phishing', False)
                    confidence = api_result.get('confidence', 0)
                    source = api_result.get('source', 'unknown')
                    
                    url_info['phishing_detection'] = {
                        'is_phishing': is_phishing,
                        'confidence': confidence,
                        'source': source
                    }
                    
                    if is_phishing:
                        url_info['suspicious'] = True
                        url_info['reason'] = f'Detected as phishing by {source} (confidence: {confidence*100:.1f}%)'
                        
                        self.suspicious_indicators.append({
                            'type': 'url',
                            'name': 'Phishing URL Detected',
                            'description': f'URL flagged as phishing by {source}: {url}',
                            'severity': 'critical'
                        })
                        
                        # Add to URL analysis results
                        self.url_analysis_results.append({
                            'url': url,
                            'is_phishing': True,
                            'confidence': confidence * 100,
                            'source': source
                        })
                    else:
                        self.url_analysis_results.append({
                            'url': url,
                            'is_phishing': False,
                            'confidence': confidence * 100,
                            'source': source
                        })
                else:
                    print(f"API check returned error or no result for: {url}")
                    
            except Exception as api_error:
                print(f"Error checking URL with APIs: {api_error}")
                self.errors.append({
                    'type': 'url_check',
                    'message': f'Could not check URL {url}: {str(api_error)}',
                    'severity': 'low'
                })
            
            # Check for suspicious TLDs
            suspicious_tlds = ['.tk', '.pw', '.cf', '.ga', '.gq', '.ml', '.buzz', '.xyz', '.top']
            for tld in suspicious_tlds:
                if parsed.netloc.lower().endswith(tld):
                    url_info['suspicious'] = True
                    url_info['reason'] += f' Uses suspicious TLD: {tld}'
                    break
            
            return url_info
            
        except Exception as e:
            url_info['suspicious'] = True
            url_info['reason'] = f'Error analyzing URL: {str(e)}'
            return url_info
    
    def _analyze_attachments(self, attachments: List[Dict]):
        """Analyze email attachments"""
        try:
            dangerous_extensions = [
                '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js',
                '.jar', '.zip', '.rar', '.7z', '.iso', '.dll', '.msi'
            ]
            
            for attachment in attachments:
                filename = attachment.get('filename', '').lower()
                filesize = attachment.get('size', 0)
                
                # Check for dangerous extensions
                for ext in dangerous_extensions:
                    if filename.endswith(ext):
                        self.suspicious_indicators.append({
                            'type': 'attachment',
                            'name': 'Dangerous Attachment',
                            'description': f'Attachment "{filename}" has dangerous extension: {ext}',
                            'severity': 'critical'
                        })
                
                # Check for double extensions
                if filename.count('.') > 1:
                    self.suspicious_indicators.append({
                        'type': 'attachment',
                        'name': 'Double Extension',
                        'description': f'Attachment uses double extension: {filename}',
                        'severity': 'high'
                    })
                
                # Check for unusual file sizes (very large or very small)
                if filesize > 10 * 1024 * 1024:  # > 10MB
                    self.suspicious_indicators.append({
                        'type': 'attachment',
                        'name': 'Large Attachment',
                        'description': f'Unusually large attachment: {filesize / (1024*1024):.1f}MB',
                        'severity': 'low'
                    })
                    
        except Exception as e:
            self.errors.append({
                'type': 'analysis',
                'message': f'Error analyzing attachments: {str(e)}',
                'severity': 'low'
            })
    
    def _check_obfuscation(self, body: str):
        """Check for obfuscation techniques"""
        try:
            # Check for HTML/Unicode obfuscation
            if '&#' in body or '%' in body:
                self.suspicious_indicators.append({
                    'type': 'obfuscation',
                    'name': 'Character Encoding',
                    'description': 'Email uses character encoding (possible obfuscation)',
                    'severity': 'medium'
                })
            
            # Check for invisible characters
            invisible_chars = ['\u200b', '\u200c', '\u200d', '\ufeff']
            for char in invisible_chars:
                if char in body:
                    self.suspicious_indicators.append({
                        'type': 'obfuscation',
                        'name': 'Invisible Characters',
                        'description': 'Email contains invisible Unicode characters',
                        'severity': 'high'
                    })
                    break
                    
        except Exception as e:
            self.errors.append({
                'type': 'analysis',
                'message': f'Error checking obfuscation: {str(e)}',
                'severity': 'low'
            })
    
    def _calculate_risk_score(self) -> int:
        """Calculate comprehensive risk score"""
        score = 0
        
        try:
            # URL phishing detection has highest weight
            phishing_urls = [u for u in self.url_analysis_results if u.get('is_phishing')]
            if phishing_urls:
                score += 40  # Critical weight for confirmed phishing URLs
            
            # Critical indicators
            critical_indicators = [i for i in self.suspicious_indicators if i['severity'] == 'critical']
            score += len(critical_indicators) * 25
            
            # High severity
            high_indicators = [i for i in self.suspicious_indicators if i['severity'] == 'high']
            score += len(high_indicators) * 15
            
            # Medium severity
            medium_indicators = [i for i in self.suspicious_indicators if i['severity'] == 'medium']
            score += len(medium_indicators) * 8
            
            # Low severity
            low_indicators = [i for i in self.suspicious_indicators if i['severity'] == 'low']
            score += len(low_indicators) * 3
            
            # Social engineering tactics
            score += len(set(self.social_engineering_tactics)) * 10
            
            return min(score, 100)
        except:
            return 50
    
    def _risk_level_from_score(self, score: int) -> str:
        """Convert score to risk level"""
        if score >= 75:
            return 'Critical Risk'
        elif score >= 50:
            return 'High Risk'
        elif score >= 25:
            return 'Medium Risk'
        elif score >= 10:
            return 'Low Risk'
        else:
            return 'Safe'
    
    def _error_response(self, message: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            'status': 'error',
            'message': message,
            'suspicious_indicators': self.suspicious_indicators,
            'extracted_urls': self.extracted_urls,
            'url_analysis_results': self.url_analysis_results,
            'errors': self.errors,
            'risk_score': 100,
            'risk_level': 'Unknown',
            'timestamp': datetime.now().isoformat()
        }


# Initialize enhanced analyzers
enhanced_header_analyzer = EnhancedEmailHeaderAnalyzer()
enhanced_content_analyzer = EnhancedEmailContentAnalyzer()


def analyze_email_headers_enhanced(headers_text: str) -> Dict[str, Any]:
    """
    Analyze email headers with enhanced detection and error handling
    
    Args:
        headers_text: Raw email headers as text
        
    Returns:
        dict: Comprehensive analysis results
    """
    return enhanced_header_analyzer.analyze(headers_text)


def analyze_email_content_enhanced(sender: str, subject: str, body: str, attachments: Optional[List[Dict]] = None) -> Dict[str, Any]:
    """
    Analyze email content with enhanced detection and REAL-TIME URL checking
    
    Args:
        sender: Sender email address
        subject: Email subject line
        body: Email body content
        attachments: Optional list of attachment information
        
    Returns:
        dict: Comprehensive analysis results including URL phishing detection
    """
    return enhanced_content_analyzer.analyze(sender, subject, body, attachments)









