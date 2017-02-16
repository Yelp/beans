import { expect } from '../../test_helper';
import UserReducer from '../../../js/reducers/user'
import { getUser, FETCH_USER } from '../../../js/actions'


describe('UserReducer', () => {
    it('handles action of getUser', () => {
        var action = {
            type: FETCH_USER,
            payload: {data: [{email:'darwin@yelp.com'}]}
        };
        expect(UserReducer([], action)[0]['email']).to.equal('darwin@yelp.com');
    });
});
