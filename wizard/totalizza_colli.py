import wizard
import decimal_precision as dp
import pooler
import time
from tools.translate import _
from osv import osv, fields
from tools.translate import _


class tempstatistiche_colli_trasporti(osv.osv):
    def _pulisci(self,cr,uid,context):
        ids = self.search(cr,uid,[])
        ok = self.unlink(cr,uid,ids,context)
        return True
    _name = 'tempstatistiche.colli.trasporti'
    _description = 'Temporaneo Stampa Trasportatori'
    _columns = {'name':fields.many2one('fiscaldoc.header', 'Documento', required=True),
                'colli':fields.float('Totale Colli', digits=(3, 2)),
                }
    def carica_doc(self, cr,uid,parametri,context):
        ok = self._pulisci(cr, uid, context)
        testa = self.pool.get('fiscaldoc.header')
        filtro_data = [('data_documento','<=', parametri.adata),('data_documento','>=', parametri.dadata)]
        testate_ids = testa.search(cr, uid, filtro_data)
        if not parametri.documenti_ids:
            raise osv.except_osv(_('ERRORE !'), _('ESCLUDERE ALMENO UNA CAUSALE DOCUMENTO'))
        if testate_ids:
            for rec_testa in testa.browse(cr, uid, testate_ids):
                for causale in parametri.documenti_ids:
                 if not causale.causale.id == rec_testa.tipo_doc.id: 
                   if rec_testa.vettore.id == parametri.carrier.id:
                    cerca = [('name','=',rec_testa.id)]
                    id_temp = self.search(cr,uid,cerca)
                    if id_temp:
                        riga_temp = self.browse(cr,uid,id_temp)[0]
                        rigawr = {'colli': rec_testa.totale_colli}
                        ok = self.write(cr,uid,id_temp,rigawr)
                    else:
                        rigawr={'name':rec_testa.id,
                                'colli': rec_testa.totale_colli}
                        ok = self.create(cr,uid,rigawr)
        return
tempstatistiche_colli_trasporti()

class parcalcolo_colli(osv.osv_memory):
    _name ='parcalcolo.colli'
    _description = 'paramentri per il calcolo dei colli assegnati al trasportatore'
    _columns = {'dadata': fields.date('Da Data Documento', required=True  ),
                'adata': fields.date('A Data Documento', required=True),
                'carrier':fields.many2one('delivery.carrier', 'Vettore', required=True),
                #'causale_ids':fields.one2many('parcalcolo.causale.colli', 'name', 'Causali da escludere', required=True),
                # 'causale_ids':fields.one2many('parcalcolo.doc', 'tipo', 'Causali da escludere', required=True),
                'documenti_ids':fields.one2many('parcalcolo.doc', 'name', 'Causale da escludere', required=True),
                #'categoria_ids':fields.one2many('parcalcolo.categorie', 'name', 'Categorie da escludere', required=True),
                }
    
    def _build_contexts(self, cr, uid, ids, data, parametri, context=None):
        if context is None:
            context = {}
        result = {}

        #CONVERTE LA DATA IN FORMATO GG/MM/AAAA
        parametri.dadata = time.strptime(parametri.dadata, "%Y-%m-%d")
        parametri.dadata=time.strftime("%d/%m/%Y",parametri.dadata)
        
        parametri.adata = time.strptime(parametri.adata, "%Y-%m-%d")
        parametri.adata=time.strftime("%d/%m/%Y",parametri.adata)
        
        result = {'dadata':parametri.dadata,'adata':parametri.adata, 'carrier':parametri.carrier.name
                  
                    }
        
    def _print_report(self, cr, uid, ids, data, parametri, context=None):
       
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['dadata',  'adata', 'carrier'])[0] #  'tipodoc', 'atipodoc' 
        parametri.dadata = time.strptime(parametri.dadata, "%Y-%m-%d")
        parametri.dadata=time.strftime("%d/%m/%Y",parametri.dadata)
        
        parametri.adata = time.strptime(parametri.adata, "%Y-%m-%d")
        parametri.adata=time.strftime("%d/%m/%Y",parametri.adata)
        used_context = {'dadata':parametri.dadata,'adata':parametri.adata, 'carrier':parametri.carrier.name
                       }
        #
        data['form']['parameters'] = used_context
        pool = pooler.get_pool(cr.dbname)
        #fatture = pool.get('fiscaldoc.header')
        active_ids = context and context.get('active_ids', [])
        Primo = True
        #import pdb;pdb.set_trace()
        return {'type': 'ir.actions.report.xml',
                'report_name': 'collitrasportatore',
                'datas': data,
                }
    def crea_temp_colli(self, cr, uid, ids, data, context=None):
        #
        righe = self.pool.get('fiscaldoc.righe')
        testa = self.pool.get('fiscaldoc.header')
        parametri = self.browse(cr,uid,ids)[0]
        ok = self.pool.get('tempstatistiche.colli.trasporti').carica_doc(cr,uid,parametri,context)
        return self._print_report(cr, uid, ids, data, parametri, context=context)
    
parcalcolo_colli()

class parcalcolo_doc(osv.osv_memory):
    _name = 'parcalcolo.doc' 
    _description = 'parametri di selezione categorie da escludere'
    _columns = {'name':fields.many2one('parcalcolo.colli','Testata Causali'),
                'causale':fields.many2one('fiscaldoc.causalidoc', 'Causali da escludere',)
                }
    



parcalcolo_doc()
