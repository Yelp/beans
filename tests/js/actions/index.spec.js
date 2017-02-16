import { expect } from '../../test_helper';
import { FETCH_METRICS, FETCH_PREFS, FETCH_USER } from '../../../js/actions/index';
import { getMetrics, getPreferences, getUser } from '../../../js/actions/index';


describe('actions', ()=> {
    describe('getMetric', ()=> {
        it('has the correct type', ()=>{
            const metrics = getMetrics('v1');
            expect(metrics.type).to.equal(FETCH_METRICS)
        });
    });
    describe('getPreferences', ()=> {
        it('has the correct type', ()=>{
            const metrics = getMetrics('v1');
            expect(metrics.type).to.equal(FETCH_METRICS)
        });
    });
    describe('getUser', ()=> {
        it('has the correct type', ()=>{
            const metrics = getMetrics('v1');
            expect(metrics.type).to.equal(FETCH_METRICS)
        });
    });
});
