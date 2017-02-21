import { expect } from '../../test_helper';
import PrefReducer from '../../../js/reducers/preferences'
import { getPrefs, FETCH_PREFS } from '../../../js/actions'


describe('PrefReducer', () => {
    it('handles action of getPrefs', () => {
        var action = {
            type: FETCH_PREFS,
            payload: {data: [{title:'metrics'}]}
        };
        expect(PrefReducer([], action)[0]['title']).to.equal('metrics');
    });
});
