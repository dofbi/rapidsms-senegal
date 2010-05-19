'''
Created on 9 mars 2010

@author: alioune
'''
from sgmllib import SGMLParser
import htmlentitydefs
import re
class BaseHTMLProcessor (SGMLParser):
        def reset (self):
                SGMLParser.reset (self)
        def unknow_starttag (self ,tag ,attrs ):
                attributes="%s=%s" (key ,value) \
                         for key, value in attrs 
                self.pieces.append ("<%(tag)s %(attrs)>"%locals)
        def unknown_endtag (self, tag):
                self.pieces.append ("</%(tag)s>")
                
        def handle_entitydefs (self , ref):
                self.pieces.append ("&%(ref)s")
                if htmlentitydefs.entitydefs.has_key(ref):
                        self.pieces.append (";")
                else :
                    pass
                
        def handle_charref (self, ref):
            self.pieces.append ("&# %(ref)s" %locals ())
        def handle_data (self, data):
            self.pieces.append (data)
        def handle_comment (self, text):
            self.pieces.append ("<!--%(text) -->"%locals ())
            
        def handle_decl(self, decl ):
           self.pieces.append ("<! %(decl)>"%locals ()) 
        def hanlde_pi (self,pi ):
           self.pieces.append ("<? %(pi)>"% locals ())
        def output (self):
           return "".join (self.pieces)
import re   
class  Dialetizer (BaseHTMLProcessor):
     sub =()
     PWD_PROTECTED = ()
     def reset (self):
            BaseHTMLProcessor.reset(self)
     def start_pre (self):
            self.unknown_endtag(self)
     def end_pre (self):
            self.end_tag (self, "pre")
     def handle_pre(self ,text ):
            self.handle_starttag (
                    self.verbatim and text or self.processing (text))
     def processing (self , text):
            for from_pattern,to_pattern  in self.subs:
                     text =re.sub (from_pattern , to_pattern)
            return text 
        
                    
                        
                