/** @odoo-module **/
import {patch} from "@web/core/utils/patch";
import {WebClient} from "@web/webclient/webclient";

import {useService} from "@web/core/utils/hooks";

patch(WebClient.prototype, {
    /**
     * @override
     */
    async setup() {
        super.setup();
        this.orm = useService("orm");

        const webTitle = await this.orm.call(
            "res.config.settings",
            "get_web_title",
            []
        );
        this.title.setParts({zopenerp: webTitle.web_title});
    },
});