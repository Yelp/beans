import PrefReducer from '../../../js/reducers/preferences';
import { FETCH_PREFS } from '../../../js/actions';


describe('PrefReducer', () => {
  it('handles action of getPrefs', () => {
    const action = {
      type: FETCH_PREFS,
      payload: { data: [{ title: 'metrics' }] },
    };
    expect(PrefReducer([], action)[0].title).toBe('metrics');
  });
});
