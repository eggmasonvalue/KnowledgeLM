'use strict';

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var AnnouncementXBRLFormat = function (_BlinkElement) {
    _inherits(AnnouncementXBRLFormat, _BlinkElement);

    function AnnouncementXBRLFormat(args) {
        _classCallCheck(this, AnnouncementXBRLFormat);

        var _this = _possibleConstructorReturn(this, _BlinkElement.call(this));

        var attr = B.extractArgAttrs(args);
        _this.state = new B.State({
            row: attr.row,
            data: attr.data || {}
        });

        var ann_change_data = _this.state.data['ann_change'] || [];
        var ann_auditor_data = _this.state.data['ann_auditor'] || [];
        var ann_independent_director_data = _this.state.data['ann_independent_director'] || [];
        var ann_director_details_data = _this.state.data['ann_director_details'] || [];

        var auditorFields = [{
            title: 'Name of the listed entity/ material subsidiary',
            field: 'listEntityName'
        }, {
            title: "Name of the Statutory Auditor/Firm",
            field: "statuatoryAuditorName"
        }, {
            title: "Address",
            field: "address"
        }, {
            title: "Contact Number",
            field: "contactNumber"
        }, {
            title: "Email",
            field: "email"
        }, {
            title: "Date on which the statutory auditor was appointed",
            field: "statAuditorAppointDate",
            isDateFormat: true
        }, {
            title: "Date on which the term of the statutory auditor was scheduled to expire",
            field: "statAuditorExpireDate",
            isDateFormat: true
        }, {
            title: "Date of submission of latest audit report/limited review report submitted by the auditor - Prior to resignation",
            field: "submisionAuditReportDate",
            isDateFormat: true
        }, {
            title: "Period for which Audit Report/Limited review report is required to be prepared by the resigning Auditor as per date the of resignation",
            field: "auditReportPeriod"
        }, {
            title: "Detailed reason for resignation",
            field: "resignationReason"
        }, {
            title: "In  case  of  any  concerns,  efforts  made  by  the  auditor  prior  to  resignation (including approaching the Audit Committee/Board of Directors along with the date of communication made to the Audit Committee/Board of Directors)",
            field: "auditorPriorResignation"
        }, {
            title: "Whether the inability to obtain sufficient appropriate audit evidence was due to a management-imposed limitation or circumstances beyond the control of the management",
            field: "whethInabilityControlMgnt"
        }, {
            title: "Whether the  lack of  information  would  have significant  impact  on  the financial statements/results of Listed entity as well as Material Subsidiary.",
            field: "whethResMaterialSubsidiary"
        }, {
            title: "Whether the  auditor  has  performed  alternative  procedures  to  obtain appropriate  evidence  for  the  purposes  of  audit/limited  review  as  laid down in SA 705 (Revised)",
            field: "whethReviewLaiddownSa"
        }, {
            title: "Whether the lack of information was prevalent in the previous reported financial   statements/results. If yes, on what basis the previous audit/limited review reports were issued. (comment in company remarks field)",
            field: "whethReviewReportIssue"
        }, {
            title: "Company Remarks (if any)",
            field: "compRemark"
        }, {
            title: "Remarks",
            field: "remark"
        }];

        var changeFields = [{
            title: "Reason of Changes",
            field: "reasonChange"
        }, {
            title: "Designation",
            field: "designation"
        }, {
            title: "Name of the Entity",
            field: "auditorName"
        }, {
            title: "Effective Date",
            field: "effectiveReginationDate",
            isDateFormat: true
        }, {
            title: "Term of Appointment",
            field: "appointmentTerm"
        }, {
            title: "Brief Profile",
            field: "profile"
        }, {
            title: "Disclosure  of  relationships  between  directors  (in  case  of  appointment  of  a director)",
            field: "discRelationBetDirector"
        }, {
            title: "Confirmation in compliance with SEBI Letter dated June 14, 2018 read along with NSE Circular dated June 20, 2018",
            field: "confCompSebiLetter"
        }, {
            title: "Reason of Resignation/ Removal/Disqualification/Cessation/Vacation of office due to statutory authority order",
            field: "resignationReason"
        }, {
            title: "Entity whose Auditor Resigned/Ceased/Removed",
            field: "auditorResignedEntity"
        }, {
            title: "Current Designation",
            field: "currentDesignation"
        }, {
            title: "Additional/new Designation",
            field: "newDesignation"
        }, {
            title: "Remarks",
            field: "txadRemark"
        }];

        var independentFields = [{
            title: "Name of the Director",
            field: "directorName"
        }, {
            title: "Effective date of resignation",
            field: "effectiveReginationDate",
            isDateFormat: true
        }, {
            title: "Whether the confirmation from the resigning director that there is no other material reason other than those provided for resignation is received from the director.",
            field: "whethConfirmResignReason"
        }, {
            title: "Company Remarks (if any)",
            field: "compRemark"
        }, {
            title: "Remarks",
            field: "remark"
        }];

        function format(val) {
            if (!val) val = '-';
            return td({ class: 'ps-1' }, val);
        }
        function formatDate(val) {
            if (!val) {
                val = '-';
            } else {
                val = val.split(' ')[0];
            }
            return td({ class: 'ps-1' }, val);
        }

        // This getRows method will create the table row element (tr) with respect of give data array and field array
        // given the params
        var getRows = function getRows(dataArr, fieldArr) {
            var trs = [];
            if (dataArr.length) {
                fieldArr.forEach(function (ele) {
                    var fieldTitle = ele.title;
                    var field = ele.field;
                    var isDateFormat = ele.isDateFormat ? true : false;
                    var rowspanVal = dataArr.length > 0 ? dataArr.length : 'none';
                    trs.push(tr(td({ width: "40%" }, { rowspan: rowspanVal }, fieldTitle), isDateFormat == true ? formatDate(dataArr[0][field]) : format(dataArr[0][field])));
                    if (dataArr.length > 0) {
                        dataArr.slice(1).forEach(function (element) {
                            trs.push(tr(isDateFormat == true ? formatDate(element[field]) : format(element[field])));
                        });
                    }
                });
            } else {
                trs.push(tr(td({ class: 'text-center emptyRow' }, { colspan: 2 }, 'No Records')));
            }
            return [].concat(trs);
        };

        var getAnnChangeTable = function getAnnChangeTable() {
            return div({ class: 'col table-wrap' }, table({ class: 'common_table customHeight-table table table-bordered' }, thead(tr(th({ colspan: 2 }, 'DETAILS OF CHANGE'))), tbody(getRows(ann_change_data, changeFields))));
        };

        var getAnnAuditorTable = function getAnnAuditorTable() {
            return div({ class: 'col table-wrap' }, table({ class: 'common_table customHeight-table table table-bordered' }, thead(tr(th({ colspan: 2 }, 'DETAILS OF CHANGE'))), tbody(getRows(ann_auditor_data, auditorFields))));
        };

        var getAnnIndependentDirectorTable = function getAnnIndependentDirectorTable() {
            return div({ class: 'col table-wrap' }, table({ class: 'common_table customHeight-table table table-bordered' }, thead(tr(th({ colspan: 2 }, 'DETAILS OF CHANGE'))), tbody(getRows(ann_independent_director_data, independentFields))));
        };

        var getAnnDirectorDetailsTable = function getAnnDirectorDetailsTable() {
            return div({ class: 'col table-wrap' }, table({ class: 'common_table customHeight-table table table-bordered' }, thead(tr(th({ width: "30%" }, 'Name of Companies'), th({ width: "30%" }, 'Category of directorship'), th({ width: "40%" }, 'Membership of board committees'))), tbody(AnnDirectorDetailRow())));
        };

        var AnnDirectorDetailRow = function AnnDirectorDetailRow() {
            var trs = [];
            if (validArray(ann_director_details_data)) {
                ann_director_details_data.forEach(function (element) {
                    trs.push(tr(format(element.companiesNames), format(element.directshipCategory), format(element.boardCommiMembership)));
                });
            } else {
                trs.push(tr(td({ class: 'text-center emptyRow' }, { colspan: 3 }, 'No Records')));
            }
            return trs;
        };

        var addAnnChangeTable = function addAnnChangeTable() {
            return div({ class: 'h4 mb-2 pt-3 section-heading tableTitle' }, 'Change in Directors/ Key Managerial Personnel/ Auditor/ Compliance Officer/ Share Transfer Agent');
        };
        var addAnnAuditorTable = function addAnnAuditorTable() {
            return div({ class: 'h4 mb-2 pt-3 section-heading tableTitle' }, 'Resignation of Statutory Auditor');
        };
        var addAnnIndependentDirectorTable = function addAnnIndependentDirectorTable() {
            return div({ class: 'h4 mb-2 pt-3 section-heading tableTitle' }, 'Resignation of Independent director');
        };
        var addAnnDirectorDetailsTable = function addAnnDirectorDetailsTable() {
            return div({ class: 'h4 mb-2 pt-3 section-heading tableTitle' }, 'DIRECTORSHIP DETAILS');
        };

        var validArray = function validArray(arr) {
            return arr && arr.length && arr.length > 0 ? true : false;
        };

        var c1 = validArray(ann_change_data);
        var c2 = validArray(ann_auditor_data);
        var c3 = validArray(ann_independent_director_data);
        var c4 = validArray(ann_director_details_data);
        // There are 4 blocks with respective tables. And they will be display if it's respective data array has values / non-empty
        // 1. Change in Directors/ Key Managerial Personnel/ Auditor/ Compliance Officer/ Share Transfer Agent
        // 2. Resignation of Statutory Auditor
        // 3. Resignation of Independent director
        // 4. DIRECTORSHIP DETAILS
        var dom = div({ class: 'my-3' }, 'No Data Available');
        if (c1 || c2 || c3 || c4) {
            dom = div({}, c1 ? addAnnChangeTable() : '', div({ class: 'row' }, c1 ? getAnnChangeTable() : ''), c2 ? addAnnAuditorTable() : '', div({ class: 'row' }, c2 ? getAnnAuditorTable() : ''), c3 ? addAnnIndependentDirectorTable() : '', div({ class: 'row' }, c3 ? getAnnIndependentDirectorTable() : ''), c4 ? addAnnDirectorDetailsTable() : '', div({ class: 'row' }, c4 ? getAnnDirectorDetailsTable() : ''));
        }

        //mandatory code for a BlinkUI component
        _this.args = dom.args;
        _this.elem = dom.elem;
        _this.elem.cmp = _this;
        //mandatory code for a BlinkUI component ends
        return _this;
    }

    return AnnouncementXBRLFormat;
}(BlinkElement);

instantiate('AnnouncementXBRLFormat', AnnouncementXBRLFormat);