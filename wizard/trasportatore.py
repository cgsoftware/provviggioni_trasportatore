import wizard
import decimal_precision as dp
import pooler
import time
from tools.translate import _
from osv import osv, fields
from tools.translate import _

class tempstatistiche_trasporti(osv.osv):
    def _pulisci(self,cr,uid,context):
        ids = self.search(cr,uid,[])
        ok = self.unlink(cr,uid,ids,context)
        return True
    _name = 'tempstatistiche.trasporti'
    _description = 'Temporaneo Stampa Trasportatori'
    _columns = {'name':fields.many2one('fiscaldoc.header', 'Documento', required=True),
                'imponibile':fields.float('Imponibile', digits=(12,2)),
                'prov1':fields.float('Proviggione1', digits=(3, 2)),
                'prov2':fields.float('Proviggione2', digits=(3, 2)),
                'zona':fields.char('Zona', size=20) 
                }
    def mappa_categoria(self, cr, uid, categoria, context):
        categ = categoria.child_id
        # 
        lista_id=[]
        lista_id.append(categoria.id)
        if categ:
            for riga in categ:
                lista_id.append(riga.id)
           
            #import pdb;pdb.set_trace()
                if riga.child_id:
                    sottocateg=riga.child_id
                    for new in sottocateg:
                        lista_id.append(new.id)
            return lista_id

    def carica_doc(self, cr,uid,parametri,context):
        ok = self._pulisci(cr, uid, context)
        #lista_id = self.mappa_categoria(cr, uid, parametri, context)
        testa = self.pool.get('fiscaldoc.header')
        
        filtro_data = [('data_documento','<=', parametri.adata),('data_documento','>=', parametri.dadata)]
        testate_ids = testa.search(cr, uid, filtro_data)
        lista_id = []
        import pdb;pdb.set_trace()
        if testate_ids:
            for rec_testa in testa.browse(cr, uid, testate_ids):
                if parametri.causale_ids:
                 for causale in parametri.causale_ids:
                    
                  if not causale.causale.id == rec_testa.tipo_doc.id:
                  #import pdb;pdb.set_trace()
                   if rec_testa.vettore.id == parametri.carrier.id:
                    #cerca = [('id','=',rec_testa.id)]
                    #id_temp = self.search(cr,uid,cerca)
                    #import pdb;pdb.set_trace()
                    if rec_testa.partner_indcons_id.city == rec_testa.partner_indfat_id.city:
                        if rec_testa.partner_indfat_id.city == parametri.zona1.name:
                            #LA ZONA DI CONSEGNA E' UGUALE ALLA ZONA DI FATTURAZIONE DEL PARTNER
                            #ED ENTRAMBE SONO UGUALI ALLA ZONA NR.1
                            
                            
                            for riga_categ in parametri.categoria_ids:
                                    #HO UNA CATEGORIA DA ESCLUDERE DAL CALCOLO PROVVIGGIONALE
                                    lista_id = lista_id + self.mappa_categoria(cr, uid, riga_categ.categoria, context)
                                
                                    for riga_doc in rec_testa.righe_articoli:
                                        if not riga_doc.product_id.product_tmpl_id.categ_id.id in lista_id:
                                            #RIGA GIA' ESISTENTE
                                            cerca = [('name','=',rec_testa.id)]
                                            id_temp = self.search(cr,uid,cerca)
                                            #import pdb;pdb.set_trace()
                                            if id_temp:
                                               
                                                riga_temp = self.browse(cr,uid,id_temp)[0]
                                                imponibile = riga_temp.imponibile+riga_doc.totale_riga
                                                rigawr ={'imponibile':imponibile,
                                                         'prov1':imponibile*parametri.perc1/100,
                                                         }
                                                ok = self.write(cr,uid,id_temp,rigawr)
                                            else:
                                                #NUOVA RIGA
                                                imponibile = riga_doc.totale_riga
                                                rigawr={'name':rec_testa.id,
                                                       'imponibile':imponibile,
                                                       'prov1':imponibile*parametri.perc1/100,
                                                       'zona':rec_testa.partner_indfat_id.city        
                                                      }
                                                ok = self.create(cr,uid,rigawr)
                                                
                            
                        else:
                            
                            for riga_categ in parametri.categoria_ids:
                                lista_id = lista_id + self.mappa_categoria(cr, uid, riga_categ.categoria, context)
                            for riga_doc in rec_testa.righe_articoli:
                             
                                if not riga_doc.product_id.product_tmpl_id.categ_id.id in lista_id:
                                            cerca = [('name','=',rec_testa.id)]
                                            id_temp = self.search(cr,uid,cerca)
                                            #RIGA GIA' ESISTENTE
                                            if id_temp:
                                                riga_temp = self.browse(cr,uid,id_temp)[0]
                                                imponibile = riga_temp.imponibile+riga_doc.totale_riga
                                                rigawr ={'imponibile':imponibile,
                                                         'prov2':imponibile*parametri.perc2/100,
                                                         }
                                                ok = self.write(cr,uid,id_temp,rigawr)
                                            else:
                                                #NUOVA RIGA
                                                imponibile = riga_doc.totale_riga
                                                rigawr={'name':rec_testa.id,
                                                       'imponibile':imponibile,
                                                       'prov2':imponibile*parametri.perc2/100,
                                                       'zona':rec_testa.partner_indcons_id.city        
                                                       }
                                                ok = self.create(cr,uid,rigawr)
                                                


                    else:
                        
                        if rec_testa.partner_indcons_id.city == parametri.zona1.name:
                            
                            for riga_categ in parametri.categoria_ids:
                                lista_id = lista_id + self.mappa_categoria(cr, uid, riga_categ.categoria, context)
                            for riga_doc in rec_testa.righe_articoli:
                                        if not riga_doc.product_id.product_tmpl_id.categ_id.id in lista_id:
                                            cerca = [('name','=',rec_testa.id)]
                                            id_temp = self.search(cr,uid,cerca)
                                            if id_temp:
                                                riga_temp = self.browse(cr,uid,id_temp)[0]
                                                imponibile = riga_temp.imponibile+riga_doc.totale_riga
                                                rigawr ={'imponibile':imponibile,
                                                         'prov1':imponibile*parametri.perc1/100,
                                                         }
                                                ok = self.write(cr,uid,id_temp,rigawr)
                                            else:
                                                #NUOVA RIGA
                                                imponibile = riga_doc.totale_riga
                                                rigawr={'name':rec_testa.id,
                                                       'imponibile':imponibile,
                                                       'prov1':imponibile*parametri.perc1/100,
                                                       'zona':rec_testa.partner_indcons_id.city        
                                                       }
                                                ok = self.create(cr,uid,rigawr)
                        
                        else:
                           # import pdb;pdb.set_trace()
                            for riga_categ in parametri.categoria_ids:
                                lista_id = lista_id + self.mappa_categoria(cr, uid, riga_categ.categoria, context)
                            for riga_doc in rec_testa.righe_articoli:
                                if not riga_doc.product_id.product_tmpl_id.categ_id.id in lista_id:
                                            cerca = [('name','=',rec_testa.id)]
                                            id_temp = self.search(cr,uid,cerca)
                                            if id_temp:
                                                riga_temp = self.browse(cr,uid,id_temp)[0]
                                                imponibile = riga_temp.imponibile+riga_doc.totale_riga
                                                rigawr ={'imponibile':imponibile,
                                                         'prov2':imponibile*parametri.perc2/100,
                                                         }
                                                ok = self.write(cr,uid,id_temp,rigawr)
                                            else:
                                                #NUOVA RIGA
                                                imponibile = riga_doc.totale_riga
                                                rigawr={'name':rec_testa.id,
                                                       'imponibile':imponibile,
                                                       'prov2':imponibile*parametri.perc2/100,
                                                       'zona':rec_testa.partner_indcons_id.city        
                                                       }
                                                ok = self.create(cr,uid,rigawr)
                else:
                    raise osv.except_osv(_('ERRORE !'), _('ESCLUDERE ALMENO UNA CAUSALE DOCUMENTO'))                                
        return
                        
                            
                            
        
    
tempstatistiche_trasporti()
                


class parcalcolo_trasporti(osv.osv_memory):
    _name ='parcalcolo.trasporti'
    _description = 'paramentri per il calcolo dei corrispettivi al trasportatore'
    _columns = {'dadata': fields.date('Da Data Documento', required=True  ),
                'adata': fields.date('A Data Documento', required=True),
                'carrier':fields.many2one('delivery.carrier', 'Vettore', required=True),
                'zona1':fields.many2one('res.city','Zona A', required=True),
                'perc1':fields.float('Percentuale Zona A', digits=(3, 2), required=True),
                'zona2':fields.many2one('res.city','Zona B'),
                'perc2':fields.float('Percentuale Zona B', digits=(3, 2)),
                'categoria_ids':fields.one2many('parcalcolo.categorie', 'name', 'Categorie da escludere', required=True),
                
                'causale_ids':fields.one2many('parcalcolo.causale', 'name', 'Causali da escludere', required=True),
                }
    def _build_contexts(self, cr, uid, ids, data, parametri, context=None):
        if context is None:
            context = {}
        result = {}
       
        #if data['form']['tipodoc']==0 or data['form']['tipodoc']==False:
        #     data['form']['tipodoc']=1
        #     data['form']['atipodoc']=99999
        #import pdb;pdb.set_trace()
        #CONVERTE LA DATA IN FORMATO GG/MM/AAAA
        parametri.dadata = time.strptime(parametri.dadata, "%Y-%m-%d")
        parametri.dadata=time.strftime("%d/%m/%Y",parametri.dadata)
        
        parametri.adata = time.strptime(parametri.adata, "%Y-%m-%d")
        parametri.adata=time.strftime("%d/%m/%Y",parametri.adata)
        
        result = {'dadata':parametri.dadata,'adata':parametri.adata, 'carrier':parametri.carrier.name
                  #'tipo_Stampa':parametri.tipo_Stampa
                  #'tipodoc':data['form']['tipodoc'],'atipodoc':data['form']['atipodoc'],
                  
                    }
        #import pdb;pdb.set_trace()
        return result
    
    def _print_report(self, cr, uid, ids, data, parametri, context=None):
       
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['dadata',  'adata', 'carrier'])[0] #  'tipodoc', 'atipodoc' 
        used_context = self._build_contexts(cr, uid, ids, data, parametri, context=context)
        #import pdb;pdb.set_trace()
        data['form']['parameters'] = used_context
        pool = pooler.get_pool(cr.dbname)
        #fatture = pool.get('fiscaldoc.header')
        active_ids = context and context.get('active_ids', [])
        Primo = True
        return {'type': 'ir.actions.report.xml',
                'report_name': 'trasportatore',
                'datas': data,
                }
        
    def crea_temp(self, cr, uid, ids, data, context=None):
        righe = self.pool.get('fiscaldoc.righe')
        testa = self.pool.get('fiscaldoc.header')
        parametri = self.browse(cr,uid,ids)[0]
        ok = self.pool.get('tempstatistiche.trasporti').carica_doc(cr,uid,parametri,context)
        return self._print_report(cr, uid, ids, data, parametri, context=context)
parcalcolo_trasporti()

class parcalcolo_categorie(osv.osv_memory):
    _name = 'parcalcolo.categorie' 
    _description = 'parametri di selezione categorie da escludere'
    _columns = {'name':fields.many2one('parcalcolo.trasporti','Testata parametri'),
                'categoria':fields.many2one('product.category', 'Categoria da escludere', required=True,),
                }
    



parcalcolo_categorie()

class parcalcolo_causale(osv.osv_memory):
    _name = 'parcalcolo.causale' 
    _description = 'parametri di selezione categorie da escludere'
    _columns = {'name':fields.many2one('parcalcolo.trasporti','Testata Causali'),
                'causale':fields.many2one('fiscaldoc.causalidoc', 'Causali da escludere',)
                }
    



parcalcolo_causale()