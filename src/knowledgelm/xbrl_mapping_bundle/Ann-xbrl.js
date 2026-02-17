'use strict';

var _extends = Object.assign || function (target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i]; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { target[key] = source[key]; } } } return target; };

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var xbrlTable = function (_BlinkElement) {
    _inherits(xbrlTable, _BlinkElement);

    function xbrlTable(args) {
        _classCallCheck(this, xbrlTable);

        var _this = _possibleConstructorReturn(this, _BlinkElement.call(this));

        var attr = B.extractArgAttrs(args);
        _this.state = new B.State({
            colData: attr.colData || [],
            rowData: attr.rowData || [],
            hoverColData: attr.hoverData || []
        });
        var tableHead = "";
        var quoteEquityDerivativeLink = ['FUTSTK', 'OPTSTK'];
        var quoteIndicesDerivativeLink = ['FUTIDX', 'OPTIDX'];
        var commodityType = ['FUTBLN', 'FUTENR', 'FUTAGR', 'FUTBAS', 'OPTBAS', 'Bullion Futures', 'Energy Futures', 'Agri Futures', 'Base Metal Futures', 'Base Metal Options'];
        var currencyType = ["FUTCUR", "OPTCUR", "Currency Futures", "Currency Options"];
        var IRF = ["FUTIRT", "FUTIRC", "OPTIRC", "Interest Rate Futures"];

        var sortBy = function sortBy(key, id, condt, type) {
            sortType = sortType === "asc" ? "desc" : "asc";
            if (tableHead !== key) {
                sortType = "asc";
            }
            var els = document.querySelectorAll('.toggleIcon');
            for (var i = 0; i < els.length; i++) {
                els[i].classList.remove("asc", "desc");
                els[i].parentNode.setAttribute('aria-sort', 'none');
            }
            if (condt !== null) {
                document.getElementById(condt).classList.add(sortType);
                document.getElementById(condt).parentNode.setAttribute('aria-sort', sortType === 'asc' ? 'ascending' : 'descending');
            }

            var rowSortData = _this.state.rowData.sort(sortTable(key, sortType, type));
            tableHead = key;
            _this.state.rowData = rowSortData;
        };

        var sortTable = function sortTable(key, order, type) {
            return function (a, b) {
                if (b.priority > 0 || a.priority > 0) {
                    return 0;
                }
                if (!a.hasOwnProperty(key) || !b.hasOwnProperty(key)) {
                    return 0;
                }

                var varA = void 0,
                    varB = void 0;

                if (type === "date") {
                    var month = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"];
                    var defaultDate = "01-JAN-1900";
                    var aVal = a[key] === "-" ? defaultDate.split('-') : a[key].split('-');
                    var bVal = b[key] === "-" ? defaultDate.split('-') : b[key].split('-');

                    if (aVal[1].length > 2) {
                        aVal[1] = (month.indexOf(aVal[1].toUpperCase()) + 1).toString();
                    }
                    if (bVal[1].length > 2) {
                        bVal[1] = (month.indexOf(bVal[1].toUpperCase()) + 1).toString();
                    }

                    varA = new Date(aVal.reverse().join('-'));
                    varB = new Date(bVal.reverse().join('-'));
                } else {
                    varA = typeof a[key] === 'string' ? type === "number" || type === "quantity" ? parseFloat(a[key]) : a[key].toUpperCase() : a[key];
                    varB = typeof b[key] === 'string' ? type === "number" || type === "quantity" ? parseFloat(b[key]) : b[key].toUpperCase() : b[key];
                }

                var comparison = 0;
                if (varA > varB) {
                    comparison = 1;
                } else if (varA < varB) {
                    comparison = -1;
                }
                return order === 'desc' ? comparison * -1 : comparison;
            };
        };
        var tableId = _extends({}, attr.tableStyle);
        var dom = table(tableId, thead(tr({
            onStateChange: {
                state: _this.state, obj: 'colData', onChange: function onChange(e, v) {
                    e.empty();
                    var tableHeader = _this.state.colData.map(function (col, index) {
                        if (col.sort) {
                            var indexname = (tableId.id + "col" || "orderList") + index;
                            var headContent = th({
                                width: col.width, title: col.legend && col.legend, role: 'columnheader', 'aria-sort': "none"
                            }, a({ "class": "toggleIcon", id: indexname, href: "javascript:;" }, {
                                on: {
                                    'click': function click(e) {
                                        sortBy(col.name, index, indexname, col.format || col.type);
                                    }
                                }
                            }, ""));
                            var subHeadContent = col.subHead !== "" ? '<span>' + col.subHead + '</span>' : "";
                            headContent.elem.children[0].innerHTML = col.heading + subHeadContent || '';
                            return headContent;
                        } else {
                            return th({ width: col.width }, col.heading || '', col.subHead !== "" ? span({}, col.subHead) : "");
                        }
                    });
                    B.renderAll(tableHeader, e);
                }
            }
        })), tbody({
            onStateChange: {
                state: _this.state, obj: 'rowData', onChange: function onChange(e, v) {
                    e.empty();
                    var rows = [];
                    if (_this.state.rowData.length > 0) {
                        if (_this.state.rowData[0] && _this.state.rowData[0].isloading) {
                            rows.push(tr(td({ colspan: _this.state.colData.length, class: 'text-center emptyRow' }, div({ "class": "loader-wrp" }, div({ "class": "spin-loader", "aria-hidden": "true" })))));
                        } else {
                            _this.state.rowData.forEach(function (row, t) {
                                var rowDomObj = void 0;
                                rowDomObj = tr(concatArr([{}], _this.state.colData.map(function (col, index) {
                                    if (col.section === "details") {
                                        return td({ width: col.width }, a({
                                            href: "javascript:;",
                                            on: {
                                                'click': function click(e) {
                                                    var eventType = document.getElementById("event_type").value;
                                                    var annXbrlList = ['annxbrloutcome', 'annxbrlReg30', 'annxbrlannFraud', 'annxbrlcdr', 'annxbrlshm', 'annxbrlfundRaising', 'annxbrlagr', 'annxbrlannOts', 'annaward'];
                                                    var ixbrlCheckArray = ['outcome', 'fundRaising', 'agr', 'annFraud', 'annOts', 'cdr', 'shm', 'award'];
                                                    if (eventType === 'annxbrl' || eventType === 'announcements') {
                                                        showAnnouncementXBRLPopup("#announcementXBRL_modal", row);
                                                    } else if (eventType && annXbrlList.includes(eventType.trim())) {
                                                        if (row["ixbrl"]) {
                                                            window.open(row["ixbrl"], '_blank');
                                                        } else {
                                                            showPopupXBRL("#XBRL_modal", row);
                                                        }
                                                    } else if (eventType === 'CIRP' || eventType === 'shareloss' || eventType === 'ctw') {
                                                        window.open(row["ixbrl"], '_blank');
                                                    } else {
                                                        if (eventType && ixbrlCheckArray.includes(eventType.trim()) && row["ixbrl"]) {
                                                            window.open(row["ixbrl"], '_blank');
                                                        } else {
                                                            showPopupXBRL("#XBRL_modal", row);
                                                        }
                                                    }
                                                }
                                            }
                                        }, 'Details'), p({ class: 'mt-1' }, fileSizeRender(col.fileSizeKey, row)));
                                    }
                                    if (col.name !== "today" && typeof row[col.name] === "undefined" || row[col.name] === null || row[col.name] === "-" /*|| parseFloat(row[col.name]) === 0*/) {
                                            return td({ width: col.width, class: 'text-center' }, "-");
                                        }
                                    var formatData = "";
                                    var className = "";
                                    if (typeof row[col.name] === "number") {
                                        className = "text-right";
                                        if (col.valueTyp && col.valueTyp !== null) {
                                            var dividedBy = parseInt(col.valueTyp);
                                            formatData = DecimalFixed(row[col.name] / dividedBy).toString();
                                        } else {
                                            formatData = DecimalFixed(row[col.name]).toString();
                                        }
                                    } else {
                                        if (col.name !== "today") {
                                            formatData = row[col.name].toString();
                                        }
                                    }
                                    if (col.type === "attachment") {
                                        var fileExtension = row[col.name].trim().match(/(\.\w+)$/g);
                                        fileExtension = fileExtension && fileExtension.length > 0 ? fileExtension[0] : fileExtension;
                                        if (fileExtension) {
                                            var fileIconPath = getFileIconPath(fileExtension);
                                            return td({
                                                width: col.width,
                                                class: 'text-center'
                                            }, a({
                                                href: row[col.name].toString(),
                                                target: row[col.name].substr(row[col.name].length - 4) === ".xml" ? "" : "_blank",
                                                "aria-label": row[col.title] + ' ATTACHMENT',
                                                title: row[col.title] + ' ATTACHMENT'
                                            }, {
                                                on: {
                                                    'click': function click(e) {
                                                        downloadXBRL(row[col.name].toString(), e);
                                                    }
                                                }
                                            }, img({ src: fileIconPath, alt: row[col.title] + ' ATTACHMENT', height: "22", width: "18" }, "")), p({ class: 'mt-1' }, fileSizeRender(col.fileSizeKey, row)));
                                        } else {
                                            return td({ width: col.width, class: 'text-center' }, "-");
                                        }
                                    }

                                    if (col.name === "broadcastDateTime") {
                                        return td({ width: col.width, class: "text-center" }, a({ href: "javascript:;", class: "show_link" }, row[col.name] || "-", div({ class: "hover_table" }, HoverTable({
                                            tableStyle: { width: "100%" },
                                            colData: _this.state.hoverColData || [],
                                            rowData: row || [],
                                            isHover: true
                                        }))));
                                    }
                                    if (col.heading.toLowerCase() === "symbol" && row['priority'] !== 1) {
                                        if (IRF.indexOf(row["instrument"]) !== -1 || IRF.indexOf(row["instrumentType"]) !== -1) {
                                            return td({ width: col.width }, a({
                                                href: "/interest-rate-future-getquote?symbol=" + encodeURIComponent(row[col.name]) + "&identifier=" + row.identifier,
                                                target: "_blank"
                                            }, row[col.name]));
                                        } else if (quoteEquityDerivativeLink.indexOf(row["instrumentType"]) !== -1) {
                                            return td({ width: col.width }, a({
                                                href: "/get-quotes/derivatives?symbol=" + encodeURIComponent(row[col.name]) + "&identifier=" + encodeURIComponent(row.identifier),
                                                target: "_blank"
                                            }, row[col.name]));
                                        } else if (quoteIndicesDerivativeLink.indexOf(row["instrumentType"]) !== -1) {
                                            return td({ width: col.width }, a({
                                                href: "/get-quotes/derivatives?symbol=" + encodeURIComponent(row[col.name]) + "&identifier=" + encodeURIComponent(row.identifier),
                                                target: "_blank"
                                            }, row[col.name]));
                                        } else if (currencyType.indexOf(row["instrumentType"]) !== -1) {
                                            return td({ width: col.width }, a({
                                                href: "/currency-getquote?identifier=" + encodeURIComponent(row['identifier']),
                                                target: "_blank"
                                            }, row[col.name]));
                                        } else if (commodityType.indexOf(row["instrumentType"]) !== -1) {
                                            return td({ width: col.width }, a({
                                                href: "/commodity-getquote?symbol=" + encodeURIComponent(row[col.name]) + "&expiryDate=" + encodeURIComponent(row.expiryDate) + "&instrumentType=" + encodeURIComponent(row.instrumentType),
                                                target: "_blank"
                                            }, row[col.name]));
                                        } else {
                                            if (col.quoteType && col.quoteType === bondsKey) {
                                                return td({ width: col.width }, a({
                                                    href: '/get-quotes/' + col.quoteType + '?symbol=' + encodeURIComponent(row[col.name]) + '&series=' + encodeURIComponent(row['series']) + '&maturityDate=' + encodeURIComponent(row['maturity_date']),
                                                    target: "_blank"
                                                }, row[col.name]));
                                            }
                                            return td({ width: col.width }, a({
                                                href: "/get-quotes/" + (col.quoteType || getEquityType(row.meta)) + "?symbol=" + encodeURIComponent(row[col.name]),
                                                target: "_blank"
                                            }, row[col.name]));
                                        }
                                    } else {
                                        return td({ width: col.width, class: className }, formatData);
                                    }
                                })));
                                rows.push(rowDomObj);
                            });
                        }
                    } else {
                        rows.push(tr(td({ colspan: _this.state.colData.length, class: 'text-center emptyRow' }, 'No Records')));
                    }
                    B.renderAll(rows, e);
                }
            }
        }));
        //mandatory code for a BlinkUI component
        _this.args = dom.args;
        _this.elem = dom.elem;
        _this.elem.cmp = _this;
        //mandatory code for a BlinkUI component ends
        return _this;
    }

    return xbrlTable;
}(BlinkElement);

instantiate('xbrlTable', xbrlTable);

// Populate the dropdown with table names
var selectkeyMapping = {
    "Rec20BonusShare": "Bonus Share",
    "Rec40Dividend": "Dividend",
    "Rec50VoluntaryDelist": "Voluntary Delisting",
    "Rec30BuyBAck": "Buy Back",
    "AlterationOfCapitalRecord30": "Alteration of Capital",
    "AlterationOfExistSecRecord40": "Alteration of Terms or Structure of any existing Securities",
    "RestrictionOfSecRecord50": "Any Restriction on Transferability of Securities",
    "AllotmentOfSecRecord60": "Allotments of Securities",
    "IssuanceOfSecuritiesRecord20": "Issuance of Securities",
    "RecUnitEventSlumpSale": "Other Restructuring",
    "Rec140Reg30Update": "Rec 30 Update",
    "RecDetailsAmalagation": "Amalgamation OR Merger",
    "Rec60EventTypeAcquistion": "Acquistion",
    "RecEventTypeDemerger": "De-Merger",
    "RecEventSlumpSale": "Slump sale",
    "Rec50DetailsDemerger": "Details of Division for Event Type Demerger",
    "RecSalesdisposal": "Sale Or Disposal",
    "Rec20EventAmalagationMerge": "Event type Amalgamation/Merger",
    "Rec90EventTypeIncorporation": "Incorporation",
    "Rec20InitialDisclosure": "Details of Shareholders Meeting",
    "Rec30SubsequentDisclosure": "Details of Resolution/Agenda",
    "Rec20InitialDisclosureAnnFraud": "Initial Disclosure",
    "Rec30SubsequentDisclosureAnnFraud": "Subsequent Disclosure",
    "Rec30SubsequentCDR": "Subsequent Disclosure",
    "Rec20InitialCDR": "Initial Disclosure",
    "XbrlRec60Response": "Others",
    "XbrlRec50Response": "Termination of Agreement",
    "XbrlRecExeAgr": "Execution of Agreement",
    "XbrlRec40Response": "Revision or Amendments of Agreement",
    "Rec20InterCreditors": "Inter - Creditors Agreement",
    "Rec30OneTimeSettlement": "One time Settlement",
    "Rec20ISDPreOpenBuyback": "Pre Issue Stage",
    "Rec30ISDPostOpenBuyback": "Post Issue Stage",
    "Rec30ISDPostTenderBuyback": "Buy back Post Issue Stage",
    "Rec20ISDPreTenderBuyback": "Buy back Pre Issue Stage",
    "RecISDTakeoverPre": "Open Offer - Pre tendering phase",
    "masterRemarkOpenOfferPost": "Open Offer - Post tendering phase",
    "isdPreVoluntaryMaster": "Pre Tendering Phase",
    "isdPostVoluntaryMaster": "Post Tendering Phase"
};
var keyMapping = {
    'amlOrMergerFalInRelPartyTran_Rec20EventAmalagationMerge': 'Whether the Amalgamation/Merger would fall within Related Party Transactions',
    'dateOfBMForAmlInRPTAppTkn_Rec20EventAmalagationMerge': 'Date of board meeting in which RPT approval taken',
    'dtAuditCMForAmlInRPTAppTake_Rec20EventAmalagationMerge': 'Date of audit committee meeting in which RPT approval taken',
    'whAmlOrMERPTIsMaterial_Rec20EventAmalagationMerge': 'Whether the said RPT is material',
    'dateOfApprvlOfAmlOrMEFrmSH_Rec20EventAmalagationMerge': 'Date of approval from shareholder',
    'dtIntstInTheEntBeingAml_Rec20EventAmalagationMerge': "Whether the promoter/promoter group/associate/holdings/subsidary companies/Director and KMP and it's relative has interest in the entity being acquired",
    'natureIntrstDtls_Rec20EventAmalagationMerge': 'Nature of interest and details thereof',
    'whAmlOrMergerIsDoneAtArmsLen_Rec20EventAmalagationMerge': 'Whether the same is done in arm length',
    'dateOfSpecialRes_Rec20EventAmalagationMerge': 'Date of special resolution ',
    'areaOfBusiOfTheEntis_Rec20EventAmalagationMerge': 'Area of business of the entity',
    'rationaleForAmlOrMerger_Rec20EventAmalagationMerge': 'Rationale for Amalgamation/merger',
    'natureOfConsiForAmlOrMerger_Rec20EventAmalagationMerge': 'Consideration',
    'detailsOfConsiForAmlOrMerger_Rec20EventAmalagationMerge': 'Details of consideration',
    'dtlsChgSHPLstdEntAmlOrMerger_Rec20EventAmalagationMerge': 'Brief details of change in shareholding pattern of listed entity.',
    'anyOtherBrfSIForAmlOrMerger_Rec20EventAmalagationMerge': 'Any other significant information.',
    'nameOfTheAmlEntity_Rec30DetailsAmalagationMerge': 'Name of the entity',
    'typeOfAmlEntity_Rec30DetailsAmalagationMerge': 'Type of the entity',
    'relatOfAmlEntityWithLstEnt_Rec30DetailsAmalagationMerge': 'Relationship with listed entity',
    'dtlsOfOthrRelatAmlEntLstEnt_Rec30DetailsAmalagationMerge': 'Details of other relations',
    'preBbNumShUndrPPGCtgAmlOrME_Rec30DetailsAmalagationMerge': 'Promoter group Number of shares',
    'preBbPrctgShUndrPPGCtg_Rec30DetailsAmalagationMerge': 'Promoter group percentage',
    'preBbNumOfShUndrPublicCtg_Rec30DetailsAmalagationMerge': 'Public Number of shares ',
    'preBbPrcntgeOfShUndrPblcCtg_Rec30DetailsAmalagationMerge': 'Public Percentage',
    'preBbNumOfShUndrOtherCtg_Rec30DetailsAmalagationMerge': 'Other Number of Shares',
    'preBbPPrcntgeShUndrOthrCtg_Rec30DetailsAmalagationMerge': 'Other percentage',
    'preBbTtlNumOfShares_Rec30DetailsAmalagationMerge': 'Total Number of shares',
    'preBbTtlPPrcntgeOfShares_Rec30DetailsAmalagationMerge': 'Total percentage',
    'postBbNumOfShUndrPPGCtg_Rec30DetailsAmalagationMerge': 'Promoter group Number of shares',
    'postBbPrctgOfShUndrPPGCtg_Rec30DetailsAmalagationMerge': 'Promoter group percentage',
    'postBbNumOfShUndrPublicCtg_Rec30DetailsAmalagationMerge': 'Public Number of shares ',
    'postBbPrcntgShUndrPublicCtg_Rec30DetailsAmalagationMerge': 'Public Percentage',
    'postBbNumOfShUndrOtherCtg_Rec30DetailsAmalagationMerge': 'Other Number of shares ',
    'postBbPrcntgeShUndrOtherCtg_Rec30DetailsAmalagationMerge': 'Other percentage',
    'postBbTotalNumberOfShares_Rec30DetailsAmalagationMerge': 'Total Number of shares',
    'postBbTotalPrcntgeOfShares_Rec30DetailsAmalagationMerge': 'Total percentage',
    'ntrConsdFrDemerger_Rec40EventTypeDemerger': 'Consideration',
    'dtlsConsdFrDemerger_Rec40EventTypeDemerger': 'Details of consideration',
    'rationalFrDemerger_Rec40EventTypeDemerger': 'Rationale for demerger',
    'brfDtlChngShrPattEntDemerger_Rec40EventTypeDemerger': 'Brief details of change in shareholding pattern of all entities ',
    'whthrListBeSghtResltEnt_Rec40EventTypeDemerger': 'Whether listing would be sought for the resulting entity',
    'anyOthrBrfSignfInfoDemerger_Rec40EventTypeDemerger': 'Any other signifact information',
    'nameDemergerEnt_Rec50DetailsDemerger': 'Name of the entity',
    'typeDemergerEnt_Rec50DetailsDemerger': 'Type of the entity',
    'reltnDemergerEntWithListEnt_Rec50DetailsDemerger': 'Relationship with listed entity',
    'dtlsOthReltnDemergerEntListEnt_Rec50DetailsDemerger': 'Details of other relations',
    'preBBNumShrPrmtrDemerger_Rec50DetailsDemerger': 'Promoter group Number of shares',
    'preBBPercShrPrmtrDemerger_Rec50DetailsDemerger': 'Promoter group percentage',
    'preBBNumShrPblcDemerger_Rec50DetailsDemerger': 'Public Number of shares ',
    'preBBPercShrPblcDemerger_Rec50DetailsDemerger': 'Public Percentage',
    'preBBNumShrOthrCatDemerger_Rec50DetailsDemerger': 'Other Number of Shares',
    'preBBPerShrOthrCatDemerger_Rec50DetailsDemerger': 'Other percentage',
    'preBBTtlNumShrDemerger_Rec50DetailsDemerger': 'Total Number of shares',
    'preBBTtlPerShrDemerger_Rec50DetailsDemerger': 'Total percentage',
    'postBBNumShrPrmtrDemerger_Rec50DetailsDemerger': 'Promoter group Number of shares',
    'postBBPercShrPrmtrDemerger_Rec50DetailsDemerger': 'Promoter group percentage',
    'postBBNumShrPblcDemerger_Rec50DetailsDemerger': 'Public Number of shares ',
    'postBBPercShrPblcDemerger_Rec50DetailsDemerger': 'Public Percentage',
    'postBBNumShrOthrCatDemerger_Rec50DetailsDemerger': 'Other Number of Shares',
    'postBBPerShrOthrCatDemerger_Rec50DetailsDemerger': 'Other percentage',
    'postBBTtlNumShrDemerger_Rec50DetailsDemerger': 'Total Number of shares',
    'postBBTtlPerShrDemerger_Rec50DetailsDemerger': 'Total percentage',
    'nameAcquirer_Rec60EventTypeAcquistion': 'Name of Acquirer',
    'relationshipEntity_Rec60EventTypeAcquistion': 'Relationship of acquirer with the listed entity',
    'detailsEntity_Rec60EventTypeAcquistion': 'Details of other relation with acquirer',
    'nameTrgtEntity_Rec60EventTypeAcquistion': 'Name of the target entity',
    'turnoverTargtEntity_Rec60EventTypeAcquistion': 'Turnover of target entity',
    'proftAftrTxTrgtEnt_Rec60EventTypeAcquistion': 'PAT of target entity',
    'netWrthTargetEnt_Rec60EventTypeAcquistion': 'Networth of target entity',
    'othrFinParamTrgtEnt_Rec60EventTypeAcquistion': 'Other of target entity',
    'whthrAcqusFallWthnFrAcusEvnt_Rec60EventTypeAcquistion': 'Whether the acquistion falls under Related Party  Transaction',
    'dtBMWhchRPTTknAcqusEvnt_Rec60EventTypeAcquistion': 'Date of board meeting in which RPT approval taken',
    'dtACWhchRPTTknAcqusEvnt_Rec60EventTypeAcquistion': 'Date of audit committee meeting in which RPT approval taken',
    'whthrAcqsEvntRPTIsMatrl_Rec60EventTypeAcquistion': 'Whether the said RPT is material',
    'dtAprvlFrmShrAcqusEvnt_Rec60EventTypeAcquistion': 'Date of approval from shareholders',
    'prmtrHldngKMPAndReltIntAcqrd_Rec60EventTypeAcquistion': "Whether the promoter/promoter group/associate/holdings/subsidary companies/Director and KMP and it's relative has interest in the entity being acquired",
    'ntrIntrDtlsAcqusEvnt_Rec60EventTypeAcquistion': 'Nature of interest and details thereof',
    'whthrAcqusIsDnAtArmsLenth_Rec60EventTypeAcquistion': 'Whether the same is done in arm length',
    'dtSpclReslFrAcqusEvnt_Rec60EventTypeAcquistion': 'Date of special resolution ',
    'industryAcquirdBelongs_Rec60EventTypeAcquistion': 'Industry to which the entity being acquired belongs',
    'objctEfctAcqIncNtLmtd_Rec60EventTypeAcquistion': 'Objects and effects of acquistion',
    'whthrGovReglAprvlAcqus_Rec60EventTypeAcquistion': 'whether any govermental or regulatory approval required for acquistion ',
    'prvdBrfDtlsAntGovRegAprvlAcqus_Rec60EventTypeAcquistion': 'Provides brief details of any govermental or regulatory approvals',
    'whthrAcqsTransBeTranch_Rec60EventTypeAcquistion': 'Whether the transaction will be in branches',
    'indicativeTmPrdFrCmplAcqus_Rec60EventTypeAcquistion': 'Indicative time period for completion of the acquistion',
    'ntrConsdAcqsEvent_Rec60EventTypeAcquistion': 'Name of consideration - whether cash consideration or share swap and details of the same',
    'detlConsdAcqsEvent_Rec60EventTypeAcquistion': 'Details of considerations',
    'costAcqusPrcShrAreAcquired_Rec60EventTypeAcquistion': 'Cost of acquistion or the price at which the shares are acquired',
    'existPercShrByAcqr_Rec60EventTypeAcquistion': 'Existing percentage of shareholding held by acquirer',
    'percCtrlAcqurd_Rec60EventTypeAcquistion': 'Percentage of control acquired',
    'percAddPersists_Rec60EventTypeAcquistion': 'Percentage of shares acquired',
    'briefBGAcqrdPrdctLnBsnsAcqd_Rec60EventTypeAcquistion': 'Brief background about the entity acquired in terms of product/line of business acquired',
    'dateIncorpAcquEvent_Rec60EventTypeAcquistion': 'Date of incorporation',
    'anyOthrBrfSignfInfoAcquston_Rec60EventTypeAcquistion': 'Any other signifcant information ',
    'dtOnWhichAggrmntSaleEntr_Rec70EventTypeSalesdisposal': 'Date on which the agreement for sale has entered into',
    'expctDtOfComplSaleOrDispsl_Rec70EventTypeSalesdisposal': 'The expected date of completion of sale/disposal',
    'natrConsdFrSaleOrDispsl_Rec70EventTypeSalesdisposal': 'Consideration',
    'dtlsConsdFrSaleOrDispsl_Rec70EventTypeSalesdisposal': 'Details of consideration',
    'brfDtlBuyr_Rec70EventTypeSalesdisposal': 'Brief details of buyers',
    'slmpRPTIsMaterialSaleOrDispsl_Rec70EventTypeSalesdisposal': "Whether the promoter/promoter group/associate/holdings/subsidary companies/Director and KMP and it's relative has interest in the entity being acquired",
    'ntrIntrDtlsThrFrSaleOrDispsl_Rec70EventTypeSalesdisposal': 'Nature of interest and details thereof',
    'whthrSaleOrDispslFallwthnRPT_Rec70EventTypeSalesdisposal': 'Whether the transaction would fall within Related Party Transaction',
    'dtBMInRPTApprSaleOrDispsl_Rec70EventTypeSalesdisposal': 'Date of board meeting in which RPT approval taken',
    'dtACSaleOrDispsl_Rec70EventTypeSalesdisposal': 'Date of audit committee meeting in RPT approval taken',
    'saleOrDispslEvntRPTIsMaterial_Rec70EventTypeSalesdisposal': 'Whether the said RPT is material',
    'dtApprSaleDispslEvntFrmShrhlds_Rec70EventTypeSalesdisposal': 'Date of approval from shareholders',
    'whtrSaleOrDispslEvntAtAmrsLnth_Rec70EventTypeSalesdisposal': 'Whether the same is done at "arms length"?',
    'dtSpcResSaleOrDisps_Rec70EventTypeSalesdisposal': 'Date of special resolution',
    'anyOthrSaleOrDispsl_Rec70EventTypeSalesdisposal': 'Any other significant information',
    'dtlsSaleOrDispslListEnt_Rec80TypeSalesdisposal': 'Details of unit/Division/subsidiary',
    'typeSaleOrDispslListEnt_Rec80TypeSalesdisposal': 'Type',
    'nameSaleOrDispslListEnt_Rec80TypeSalesdisposal': 'Name of unit or division or subsidary of the listed entity',
    'prvsTurnOverSaleOrDispsListEnt_Rec80TypeSalesdisposal': 'Turnover of No. of share',
    'prvsPercTrnOverSalDispsListEnt_Rec80TypeSalesdisposal': 'Turnover percentage',
    'prvsRevenuenSaleDispslListEnt_Rec80TypeSalesdisposal': 'Revenue of No. of shares',
    'RevenuePercentage_Rec80TypeSalesdisposal': 'Revenue percentage',
    'prvsIncomOfSaleOrDispslListEnt_Rec80TypeSalesdisposal': 'Income No. of shares',
    'prvsPercIncmSaleDispslListEnt_Rec80TypeSalesdisposal': 'Income percentage',
    'prvsNtWrthSaleOrDispslListEnt_Rec80TypeSalesdisposal': 'Networth No. of shares',
    'NetworthPercentage_Rec80TypeSalesdisposal': 'Networth percentage',
    'nameOfHldngComp_Rec90EventTypeIncorporation': 'Name of the Holding Company',
    'relationOfHldng_Rec90EventTypeIncorporation': 'Relationship of Holding Company with the listed entity',
    'nameOfIncorpEnt_Rec90EventTypeIncorporation': 'Name of incorporated entity',
    'industry_Rec90EventTypeIncorporation': 'Industry to which the entity being incorporated belongs',
    'briefBgAbtTheEntIncorp_Rec90EventTypeIncorporation': 'Brief background about the entity incorporated in terms of product/line of business',
    'costOfSubscription_Rec90EventTypeIncorporation': 'Cost of subscription or the price at which the shares are subscribed',
    'percSharehldngCntrl_Rec90EventTypeIncorporation': 'Percentage of shareholding/control',
    'dateOfIncorporation_Rec90EventTypeIncorporation': 'Date of incorporation ',
    'countryInWhchListEnt_Rec90EventTypeIncorporation': 'Country in which the entity is incorporate',
    'anyOther_Rec90EventTypeIncorporation': 'Any other significant information',
    'dtOfCompletionSlumpSaleEvent_Rec100EventSlumpSale': 'Date on which agreement for sale has been entered into',
    'theOfSlmpSaleEvent_Rec100EventSlumpSale': 'The expected date of completion of slump sale',
    'natureOfSlmpSaleEvent_Rec100EventSlumpSale': 'Consideration received from such slump sale',
    'detailsOfSlmpSaleEvent_Rec100EventSlumpSale': 'Details of consideration',
    'briefOfSlmpSaleEvent_Rec100EventSlumpSale': 'Brief details of buyers',
    'whthrPrmtHldngKMPndRlt_Rec100EventSlumpSale': "Whether the promoter/promoter group/associate/holdings/subsidary companies/Director and KMP and it's relative has interest in the entity being acquired",
    'natrIntrDtlsfSlmpSaleEvent_Rec100EventSlumpSale': 'Nature of interest and details thereof',
    'whthrSlmpFallwthnRPT_Rec100EventSlumpSale': 'Whether the transaction would fall within Related Party Transaction',
    'dtBMInRPTApprSlmpSaleEvnt_Rec100EventSlumpSale': 'Date of board meeting in which RPT approval taken',
    'dtACSlmpSaleEvnt_Rec100EventSlumpSale': 'Date of audit committee meeting in RPT approval taken',
    'whthrSlmpRPTIsMaterial_Rec100EventSlumpSale': 'Whether the said RPT is material',
    'dtApprSlmpSaleEvntFrmShrhlds_Rec100EventSlumpSale': 'Date of approval from shareholders',
    'whtrSlmpSaleEvntAtAmrsLnth_Rec100EventSlumpSale': 'Whether the same is done at "arms length"',
    'dtSpcResSlmpSaleEvent_Rec100EventSlumpSale': 'Date of special resolution',
    'briefDtlsSlmpSaleEvent_Rec100EventSlumpSale': 'Brief details of change in shareholding pattern',
    'anyOthrSlmpSaleEvent_Rec100EventSlumpSale': 'Any other significant information',
    'nameOfSlumpSale_Rec110UnitEventSlumpSale': 'Name of unit or division or subsidary of the listed entity',
    'typeOfSlumpSale_Rec110UnitEventSlumpSale': 'Type of unit or division or subsidary of the listed entity',
    'areaOfSaleEntities_Rec110UnitEventSlumpSale': 'Area of business of slump sale entity',
    'prvsTurnOverOfSlmpListEnt_Rec110UnitEventSlumpSale': 'Turnover of No. of share',
    'prvsPercTrnOverOfSlmpListEnt_Rec110UnitEventSlumpSale': 'Turnover percentage',
    'prvsRevenuenSlmpListEnt_Rec110UnitEventSlumpSale': 'Revenue of No. of shares',
    'prvsPercRevenTrnOverSlmpList_Rec110UnitEventSlumpSale': 'Revenue percentage',
    'prvsIncomOfSlmpListEnt_Rec110UnitEventSlumpSale': 'Income No. of shares',
    'prvsPercIncmOfSlmpListEnt_Rec110UnitEventSlumpSale': 'Income percentage',
    'prvsPercNtWrthOfSlmpListEnt_Rec110UnitEventSlumpSale': 'Networth No. of shares',
    'dtlsPreBBSharPatFrSlmpEvnt_Rec110UnitEventSlumpSale': 'Networth percentage',
    'preBBNumShrPrmtrSlmpSaleEvnt_Rec110UnitEventSlumpSale': 'Promoter group Number of shares',
    'preBBPercShrPrmtrSlmpSaleEvnt_Rec110UnitEventSlumpSale': 'Promoter group percentage',
    'preBBNumShrPblcSlmpSaleEvnt_Rec110UnitEventSlumpSale': 'Public Number of shares ',
    'preBBPercShrPblcSlmpSaleEvnt_Rec110UnitEventSlumpSale': 'Public Percentage',
    'preBBNumShrOthrCatSlmpSaleEvnt_Rec110UnitEventSlumpSale': 'Other Number of Shares',
    'preBBPerShrOthrCatSlmpSaleEvnt_Rec110UnitEventSlumpSale': 'Other percentage',
    'preBBTtlNumShrSaleEvnt_Rec110UnitEventSlumpSale': 'Total Number of shares',
    'preBBTtlPerShrSaleEvnt_Rec110UnitEventSlumpSale': 'Total percentage',
    'postBBNumShrPrmtrSlmpSaleEvnt_Rec110UnitEventSlumpSale': 'Promoter group Number of shares',
    'postBBPercShrPrmtrSlmpSaleEvnt_Rec110UnitEventSlumpSale': 'Promoter group percentage',
    'postBBNumShrPblcSlmpSaleEvnt_Rec110UnitEventSlumpSale': 'Public Number of shares ',
    'postBBPercShrPblcSlmpSaleEvnt_Rec110UnitEventSlumpSale': 'Public Percentage',
    'postBBNumShrOthrCatSlmpEvn_Rec110UnitEventSlumpSale': 'Other Number of Shares',
    'postBBPerShrOthrCatSlmpEvn_Rec110UnitEventSlumpSale': 'Other percentage',
    'postBBTtlNumSlmpSaleEvnt_Rec110UnitEventSlumpSale': 'Total Number of shares',
    'postBBTtlPerShrSlmpSaleEvnt_Rec110UnitEventSlumpSale': 'Total percentage',
    'dtlsRsnFrOthrRestruct_Rec120EventOtherRestructuring': 'Details and reasons for restructuring',
    'quantEfctOthrRestruct_Rec120EventOtherRestructuring': 'Quantitative effect of restructuring',
    'qualtOthrRestruct_Rec120EventOtherRestructuring': 'Qualitative effect of restructuring',
    'prmtHldngKMPndRltRestruct_Rec120EventOtherRestructuring': "Whether the promoter/promoter group/associate/holdings/subsidary companies/Director and KMP and it's relative has interest in the entity being acquired",
    'dtlsBnftOthrRestruct_Rec120EventOtherRestructuring': 'Details of benefits',
    'dtlsChngShrAllOthrRestruct_Rec120EventOtherRestructuring': 'Brief details of change in shareholding pattern of all entities',
    'anyOtheSignInfoOthrRestruct_Rec120EventOtherRestructuring': 'Any other signification information',
    'nameOfRestructEnt_Rec130DetailsEvtOthrRestrctring': 'Name of the entity',
    'restrctEntRltnEntListEnt_Rec130DetailsEvtOthrRestrctring': 'Relationship with listed entity',
    'dtlsOthrRltnRestructEntListEnt_Rec130DetailsEvtOthrRestrctring': 'Details of other relation',
    'preBBNumShrPrmtrOthrRestruct_Rec130DetailsEvtOthrRestrctring': 'Promoter group Number of shares',
    'preBBPercShrPrmtrOthrRestruct_Rec130DetailsEvtOthrRestrctring': 'Promoter group percentage',
    'preBBNumShrPblcOthrRestruct_Rec130DetailsEvtOthrRestrctring': 'Public Number of shares ',
    'preBBPercShrPblcOthrRestruct_Rec130DetailsEvtOthrRestrctring': 'Public Percentage',
    'preBBNumShrOthrCatOthrRestruct_Rec130DetailsEvtOthrRestrctring': 'Other Number of Shares',
    'preBBPerShrOthrCatOthrRestruct_Rec130DetailsEvtOthrRestrctring': 'Other percentage',
    'preBBTtlNumShrOthrRestruct_Rec130DetailsEvtOthrRestrctring': 'Total Number of shares',
    'preBBTtlPerShrOthrRestruct_Rec130DetailsEvtOthrRestrctring': 'Total percentage',
    'postBBNumShrPrmtrOthrRestruct_Rec130DetailsEvtOthrRestrctring': 'Promoter group No.of shares',
    'postBBPercShrPrmtrOthrRestruct_Rec130DetailsEvtOthrRestrctring': 'Promoter group percentage',
    'postBBNumShrPblcOthrRestruct_Rec130DetailsEvtOthrRestrctring': 'Public Number of shares ',
    'postBBPercShrPblcOthrRestruct_Rec130DetailsEvtOthrRestrctring': 'Public Percentage',
    'postBBNumShrOthrCatOthrRestrct_Rec130DetailsEvtOthrRestrctring': 'Other Number of Shares',
    'postBBPerShrOthrCatOthrRestrct_Rec130DetailsEvtOthrRestrctring': 'Other percentage',
    'postBBTtlNumOthrRestruct_Rec130DetailsEvtOthrRestrctring': 'Total Number of shares',
    'postBBTtlPerShrOthrRestruct_Rec130DetailsEvtOthrRestrctring': 'Total percentage',
    'briefDtlOfInitialAnn_Rec140Reg30Update': 'Brief details of Initial Announcement',
    'reasonForUpdate_Rec140Reg30Update': 'Reason for Update',
    'transactionCompleted_Rec140Reg30Update': 'Transaction Completed',
    'amntOfTransCompl_Rec140Reg30Update': 'Amount of transaction completed',
    'dtOfTransCompl_Rec140Reg30Update': 'Date of transaction completed',
    'percOfTransComp_Rec140Reg30Update': 'Percentage of transaction completed',
    'transactDelayed_Rec140Reg30Update': 'Transaction Delayed',
    'initialDtOfCompl_Rec140Reg30Update': 'Initial date of completion',
    'revisedDate_Rec140Reg30Update': 'Revised date',
    'reasonForDelay_Rec140Reg30Update': 'Reason for delay',
    'transactionCancel_Rec140Reg30Update': 'Transaction Cancellation',
    'reasonFrCancellation_Rec140Reg30Update': 'Reason for cancellation',
    'anyLiabilOnListEnt_Rec140Reg30Update': 'Any Liability on listed entity',
    'transactionModf_Rec140Reg30Update': 'Transaction Modification',
    'otherUpdates_Rec140Reg30Update': 'Others',
    'anyOther_Rec140Reg30Update': 'Any other significant information',
    'remarksForWebsite_Rec140Reg30Update': 'Remarks',
    'decisionDate_RestrictionOfSecRecord50': 'Date of Board Meeting considering the decision for alteration of the terms or structure of any existing securities',
    'meetingCommTime_RestrictionOfSecRecord50': 'Meeting Commencement Time',
    'meetingConclTime_RestrictionOfSecRecord50': 'Meeting Conclusion Time',
    'whPIOfBMConsToSE_RestrictionOfSecRecord50': 'Whether prior intimation of board meeting considering restriction on transferability of securities given to stock exchange',
    'dateOfPIOfBMToSE_RestrictionOfSecRecord50': 'Date of prior intimation of board meeting considering restriction on transferability of securities submitted to stock exchange',
    'reasonsNonDiscBMToSE_RestrictionOfSecRecord50': 'If No, provide reason for non-disclosure ',
    'whRTSApprByBoard_RestrictionOfSecRecord50': 'Whether the restriction on transferability of securities approved by the Board',
    'reasonsRTSNotAppByBoard_RestrictionOfSecRecord50': 'If No or Deferred, provide reason  ',
    'whBDOnAgendaPriorToRTS_RestrictionOfSecRecord50': 'Whether the board discussed on the agenda item prior to deferring the proposal  restriction on transferability of securities',
    'dtlsBDOnAgendaPriorToRTS_RestrictionOfSecRecord50': 'If Yes, provide details of the discussion',
    'dtlsOrAuthIssAttProOrder_RestrictionOfSecRecord50': 'Details/Name of authority issuing attachment or prohibitory orders',
    'dtlsAndRsonAttProOrder_RestrictionOfSecRecord50': 'Brief details and reasons for attachment or prohibitory orders', 'numRegHolderTrans_RestrictionOfSecRecord50': 'Number of registered holders against whom restriction on transferability has been placed',
    'nameRegHolderTrans_RestrictionOfSecRecord50': 'Name of registered holders against whom restriction on transferability has been placed',
    'totalAffectedSecurities_RestrictionOfSecRecord50': 'Total number of securities so affected',
    'distinctiveSecNumbers_RestrictionOfSecRecord50': 'Distinctive numbers of such securities if applicable',
    'periodForOrderApplicable_RestrictionOfSecRecord50': 'Period for which order would be applicable (if stated).',
    'anyOtherDisSEBIRegCirOrProvRest_RestrictionOfSecRecord50': 'Any other disclosure w.r.t. compliance of any SEBI Act, Regulation, Circular or provision',
    'anyOtherInfoRelToRestOnTrans_RestrictionOfSecRecord50': 'Any other information',
    'remarksWDForRestOnTrans_RestrictionOfSecRecord50': 'Remarks',
    'remarksExchNotWDForRestOnTrans_RestrictionOfSecRecord50': 'Remarks for Exchange',
    'ntrOfFrdOrDfultOrArst_Rec20InitialDisclosure': 'Nature of fraud / default / arrest',
    'estmtImpctFrdOrDfltArst_Rec20InitialDisclosure': 'Estimated impact on the listed entity',
    'dtAndTimeWhnTheFrdOrDfltArst_Rec20InitialDisclosure': 'Date and time when the fraud / default / arrest was unearthing or occurred',
    'mtngInFrdOrDfltArstWsDscsd_Rec20InitialDisclosure': 'Meeting in which fraud / defaults /arrest was discussed',
    'dtMtngFrdOrDfltArstWsDscsd_Rec20InitialDisclosure': 'Date of Meeting',
    'numbOfPrsnInvlvdInFrdOrDflt_Rec20InitialDisclosure': 'Number of Person involved',
    'nameOfPrsnInvldFrdDfltOrDflt_Rec20InitialDisclosure': 'Name of Person involved',
    'estmtdAmntInvInFrdOrDflt_Rec20InitialDisclosure': 'Estimated amount involved',
    'nmAndDtlsAprAuthToWhmFrdDflt_Rec20InitialDisclosure': 'Name & Details of appropriate authorities to whom the fraud/default/arrest has been reported, if any.',
    'othrDiscWthRspctToCompSEBIAct_Rec20InitialDisclosure': 'Any other disclosure w.r.t. compliance of any SEBI Act, Regulation, Circular or provision',
    'othrInfrmFrFrdOrDflt_Rec20InitialDisclosure': 'Any other information',
    'remarkFrWebDismFrFrdOrDflt_Rec20InitialDisclosure': 'Remarks',

    'eventNoticeSHMeet_Rec20InitialDisclosure': 'Event',
    'detailsNoticeOfSHM_Rec20InitialDisclosure': 'Details of shareholders meeting',
    'modeOfSHMeet_Rec20InitialDisclosure': 'Mode of meeting',
    'numOfSHMeet_Rec20InitialDisclosure': 'Number of Shareholders Meeting',
    'dayOfSHMeet_Rec20InitialDisclosure': 'Day',
    'dateOfSHMeet_Rec20InitialDisclosure': 'Date',
    'shmCommntTime_Rec20InitialDisclosure': 'Meeting Commencement Time',
    'placeofSHMeet_Rec20InitialDisclosure': 'Place',
    'endDtOfPostalBV_Rec20InitialDisclosure': 'End date of Postal Ballot Voting',
    'numOfAgdaBT_Rec20InitialDisclosure': 'Number of agenda/business to be transacted',
    'resolutionOrAgenda_Rec20InitialDisclosure': 'Details of Resolution/Agenda',
    'otherInfoForSHMeet_Rec20InitialDisclosure': 'Any other information',
    'remarkForWDForSHMee_Rec20InitialDisclosure': 'Remarks',

    'whthrCorDebtVolOrRef_Rec20InitialCDR': 'Whether the Corporate debt Restructuring is Voluntary or Referred by Lenders/Creditors',
    'dtOfBoCdrApp_Rec20InitialCDR': 'Date of Board Meeting in which CDR was approved',
    'reaForOptCdr_Rec20InitialCDR': 'Reasons for opting CDR',
    'dtlsOfLenCredRefCdrComp_Rec20InitialCDR': 'Details of Lenders/Creditors referring Corporate Debt Restructuring of the Company',
    'dtlsOfLoanSubToCdr_Rec20InitialCDR': 'Details of the Loan to be subjected to Corporate Debt Restructuring',
    'dtlsOfCdrPro_Rec20InitialCDR': 'Brief details of the Corporate Debt Restructuring proposal',
    'anyOthDisWrtComOfSebiRegCirProIn_Rec20InitialCDR': 'Any other disclosure w.r.t. compliance of any SEBI Act, Regulation, Circular or provision',
    'anyOthInfoInitial_Rec20InitialCDR': 'Any other information',
    'websiteDissRemarksForInitial_Rec20InitialCDR': 'Remarks',
    'actAmntInvldInFrdDflt_Rec30SubsequentDisclosure': 'Actual amount involved in the fraud / defaults /arrest',
    'actImpctFrdDfltArstWsUnrthng_Rec30SubsequentDisclosure': 'Actual impact of such fraud / defaults /arrest on the listed entity and its financials',
    'corctMsrTknByLstEntOnAcc_Rec30SubsequentDisclosure': 'Corrective measures taken by the listed entity on account of such fraud / defaults /arrest',
    'mtngInwhichTheSubseqntAct_Rec30SubsequentDisclosure': 'Meeting in which the subsequent action related to  fraud / defaults /arrest was discussed',
    'dtMtngInWhichSubsqntActRlt_Rec30SubsequentDisclosure': 'Date of Meeting ',
    'statusPrcdIfAnyIntIntrnl_Rec30SubsequentDisclosure': 'Status of proceedings, if any initiated internal or at appropriate authorities',
    'othrDiscWithRspctToCompl_Rec30SubsequentDisclosure': 'Any other disclosure w.r.t. compliance of any SEBI Act, Regulation, Circular or provision',
    'othrInfoFrFrdDfltOrArst_Rec30SubsequentDisclosure': 'Any other information ',
    'remarkFrWebDismFrFrdDflt_Rec30SubsequentDisclosure': 'Remarks',
    'AO_STAGE_OF_AGRMNT_XbrlRec60Response': 'If Others, Specify stage of the agreement',
    'AO_DT_INITIAL_DISCLOSE_XbrlRec60Response': 'Date of initial disclosure of the execution of the agreement to the Stock Exchange',
    'AO_BRIEF_SUMMARY_XbrlRec60Response': 'Brief Summary of any other disclosure',
    'AO_DEATILS_REASONS_XbrlRec60Response': 'Details of reasons and impact, if any',
    'AO_OTHRDISCWRTTOSEBI_XbrlRec60Response': 'Any other disclosure w.r.t. compliance of any SEBI Act, Regulation, Circular or provision',
    'AO_OTHER_INFO_XbrlRec60Response': 'Any other information',
    'AO_REMARK_XbrlRec60Response': 'Remarks',
    'AT_DT_INT_DISCLOSURE_XbrlRec50Response': 'Date of initial disclosure of the execution of the agreement to the Stock Exchange',
    'AT_DETAIL_TERMINATE_XbrlRec50Response': 'Brief details of Termination of agreement',
    'AT_NAME_PARTIES_XbrlRec50Response': 'Name(s) of parties with whom the agreement was entered',
    'AT_NATURE_AGRMNT_XbrlRec50Response': 'Nature of the agreement',
    'AT_DT_EXC_AGRMNT_XbrlRec50Response': 'Date of execution of the agreement',
    'AT_REASON_TERM_AGRMNT_XbrlRec50Response': 'Reason for terminating the agreement',
    'AT_DETAIL_IMPACT_TERM_XbrlRec50Response': 'Details of impact of termination of the Agreement',
    'AT_OTHRDISCWRTTOSEBI_XbrlRec50Response': 'Any other disclosure w.r.t. compliance of any SEBI Act, Regulation, Circular or provision',
    'AT_OTHER_INFO_XbrlRec50Response': 'Any other information',
    'AT_REMARK_XbrlRec50Response': 'Remarks',
    'AEA_DETAILS_XbrlRec20Response': 'Brief details of the Agreement',
    'AEA_DATE_OF_BOARD_XbrlRec20Response': 'Date of Board / Committee Meeting approving the agreement',
    'AEA_PROPOSED_AGREEMENT_XbrlRec20Response': 'Whether proposed / executed agreement is in normal course of business',
    'AEA_REASONS_XbrlRec20Response': 'If No, provide reasons',
    'AEA_IMPACT_AGREEMENT_XbrlRec20Response': 'Impact of agreement on management and control of the listed entity',
    'AEA_NO_PARTIES_XbrlRec20Response': 'Number of Parties with whom agreement is entered',
    'AEA_TRANSACTION_FALL_XbrlRec20Response': 'Whether the transaction would fall under related party transactions?',
    'AEA_TRANSACTION_ARMS_XbrlRec20Response': 'Whether the transaction is done at “arms length” basis',
    'AEA_TRANSACTION_DETAIL_XbrlRec20Response': 'If No, provide details',
    'AEA_DT_OF_TRANSACTION_XbrlRec20Response': 'Date on which agreement was entered',
    'AEA_PURPOSE_XbrlRec20Response': 'Purpose of entering into the agreement',
    'AEA_SIGNIFICANT_TERM_XbrlRec20Response': 'Significant terms of the agreement (in brief) special rights like right to appoint directors, first right to share subscription in case of issuance of shares, right to restrict any change in capital structure etc.;',
    'AEA_ISSUANCE_SHARE_XbrlRec20Response': 'Whether there is any issuance / transfer of shares to the parties',
    'AEA_CLASS_SHARE_XbrlRec20Response': 'Class of shares issued/transferred',
    'AEA_ISSUE_PRICE_XbrlRec20Response': 'Issue Price per share',
    'AEA_OTHRDISCWRTTOAGR_XbrlRec20Response': 'Any other disclosures related to such agreements, viz., details of nominee on the board of directors of the listed entity, potential conflict of interest arising out of such agreements, etc;',
    'AEA_OTHRDISCWRTTOSEBI_XbrlRec20Response': 'Any other disclosure w.r.t. compliance of any SEBI Act, Regulation, Circular or provision',
    'AEA_OTHER_INFO_XbrlRec20Response': 'Any other information',
    'AEA_REMARK_XbrlRec20Response': 'Remarks',
    'AR_DT_INT_DESCLOSE_XbrlRec40Response': 'Date of initial disclosure of the execution of the agreement to the Stock Exchange',
    'AR_BRIEF_DETAILS_XbrlRec40Response': 'Brief details of Revision or amendments of agreement',
    'AR_NO_PARTIES_XbrlRec40Response': 'Number of Parties to the agreement.',
    'AR_NAME_PARTIES_XbrlRec40Response': 'Name(s) of parties with whom the agreement is entered',
    'AR_NATURE_AGRMNT_XbrlRec40Response': 'Nature of the agreement',
    'AR_DT_EXECUTION_XbrlRec40Response': 'Date of execution of the revision or amendment agreement;',
    'AR_REVISION_REASON_XbrlRec40Response': 'Reasons of Revision or amendments of agreement',
    'AR_DETAIL_IMPACT_XbrlRec40Response': 'Details of impact of the revision or amendments on the agreement',
    'AR_OTHRDISCWRTTOSEBI_XbrlRec40Response': 'Any other disclosure w.r.t. compliance of any SEBI Act, Regulation, Circular or provision',
    'AR_OTHER_INFO_XbrlRec40Response': 'Any other information',
    'AR_REMARK_XbrlRec40Response': 'Remarks',
    'disclosure_filed_Rec30OneTimeSettlement': 'Whether disclosure filed for listed company',
    'name_of_entity_Rec30OneTimeSettlement': 'Name of entity for which disclosure is filed',
    'relship_listed_comp_Rec30OneTimeSettlement': 'Relationship with the listed company',
    'disclose_defaultpay_Rec30OneTimeSettlement': 'Whether the disclosures related to defaults on payment of interest/ repayment of principal amount on loans from banks / financial institutions and unlisted debt securities was filed with Stock Exchanges as required vide SEBI circular no. SEBI/HO/CFD/CMD1/CIR/P/2019/140 dated November 21, 2019',
    'reason_disclosure_Rec30OneTimeSettlement': 'If No,  provide the reason for the same',
    'dt_disclosure_Rec30OneTimeSettlement': 'If Yes,  provide the date of disclosure',
    'meet_Rec30OneTimeSettlement': 'Meeting in which One-time Settlement (OTS) is considered, if any',
    'date_meet_Rec30OneTimeSettlement': 'Date of Meeting',
    'name_of_bank_Rec30OneTimeSettlement': 'Name of Bank(s) / Financial Institution(s) / Lender(s)',
    'dt_agreement_Rec30OneTimeSettlement': 'Date of entering / receiving the agreement / letter for settling the due',
    'amt_paid_to_agreed_Rec30OneTimeSettlement': 'Details of amount agreed to be paid by the Company',
    'dt_payment_Rec30OneTimeSettlement': 'Date of payment agreed to be made by the Company',
    'dt_payment_done_Rec30OneTimeSettlement': 'Date of payment made by the Company, if any',
    'reason_of_ots_Rec30OneTimeSettlement': 'Reasons for opting for OTS',
    'summary_Rec30OneTimeSettlement': 'Brief summary of the OTS',
    'dt_of_intimation_Rec30OneTimeSettlement': 'Date of intimation of the OTS to competent Authority, if any',
    'name_of_authority_Rec30OneTimeSettlement': 'Name and details of the Authority to whom intimation was made',
    'othrDiscwrttosebi_Rec30OneTimeSettlement': 'Any other disclosure w.r.t. compliance of any SEBI Act, Regulation, Circular or provision',
    'other_info_Rec30OneTimeSettlement': 'Any other information',
    'remarks_Rec30OneTimeSettlement': 'Remarks',
    'disclosure_filed_Rec20InterCreditors': 'Whether disclosure filed for listed company',
    'name_entity_Rec20InterCreditors': 'Name of entity for which disclosure is filed',
    'relship_listed_comp_Rec20InterCreditors': 'Relationship with the listed company',
    'inter_creditor_agrmt_Rec20InterCreditors': 'Brief details of Inter-Creditors Agreement',
    'disclose_defaultpay_Rec20InterCreditors': 'Whether the disclosures related to defaults on payment of interest/ repayment of principal amount on loans from banks / financial institutions and unlisted debt securities was filed with Stock Exchanges as required vide SEBI circular no.   SEBI/HO/CFD/CMD1/CIR/P/2019/140 dated November 21, 2019',
    'reason_disclosure_Rec20InterCreditors': 'If No,  provide the reason for the same',
    'dt_disclosure_Rec20InterCreditors': 'If Yes,  provide the date of disclosure',
    'detail_lender_Rec20InterCreditors': 'Details of Lenders',
    'amt_debt_in_ica_Rec20InterCreditors': 'Amount of debt involved in the ICA',
    'features_Rec20InterCreditors': 'Salient features, not involving commercial secrets, of the resolution / restructuring plan as decided by lenders',
    'stage_of_disclose_Rec20InterCreditors': 'Stage at which the ICA Disclosure is made (Resolution plan / Restructuring in relation to loans / borrowings from banks / financial institutions)',
    'brf_dtls_stage_of_discl_Rec20InterCreditors': 'Brief details of the Stage at which the ICA Disclosure is made',
    'othrDiscwrttosebi_Rec20InterCreditors': 'Any other disclosure w.r.t. compliance of any SEBI Act, Regulation, Circular or provision',
    'other_info_Rec20InterCreditors': 'Any other information',
    'remarks_Rec20InterCreditors': 'Remarks'
};

function displayJsonData(data, containerId) {
    var tableContainer = document.getElementById(containerId);

    console.log('containerId >>>>' + containerId);
    if (containerId === "RecDetailsAmalagation" || containerId === "RecEventTypeDemerger" || containerId === "RecSalesdisposal" || containerId === "RecUnitEventSlumpSale" || containerId === "RecEventSlumpSale" || containerId === "Rec30SubsequentDisclosure" || containerId === "XbrlRecExeAgr" || containerId === "RecSalesdisposal") {

        var tabletextContent = void 0,
            rowsData = void 0,
            tableColumnData = void 0,
            dataJson = void 0;
        if (containerId === "RecDetailsAmalagation" || containerId === "RecUnitEventSlumpSale") {
            dataJson = containerId === "RecDetailsAmalagation" ? data[0].Rec30DetailsAmalagationMerge : data[0].Rec130DetailsEvtOthrRestrctring;
            tabletextContent = containerId === "RecDetailsAmalagation" ? "Details of the entity (ies) forming part of the amalgamation/merger" : "";
            rowsData = [[{ text: "Name of Entity", rowspan: 3 }, { text: "Type of Entity", rowspan: 3 }, { text: "Relationship with listed entity(ies)", rowspan: 3 }, { text: "Details of other relations", rowspan: 3 }, { text: "Details of Pre Shareholding", colspan: 8 }, { text: "Details of Post Shareholding", colspan: 8 }], [{ text: "Promoter and Promoter Group", colspan: 2 }, { text: "Public", colspan: 2 }, { text: "Others", colspan: 2 }, { text: "Total", colspan: 2 }, { text: "Promoter and Promoter Group", colspan: 2 }, { text: "Public", colspan: 2 }, { text: "Others", colspan: 2 }, { text: "Total", colspan: 2 }], [{ text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }]];
            if (containerId === "RecDetailsAmalagation") {
                tableColumnData = [{
                    "name": "nameOfTheAmlEntity_Rec30DetailsAmalagationMerge",
                    "heading": "Name of the Entity",
                    "subHead": "",
                    "width": "10%"
                }, {
                    "name": "typeOfAmlEntity_Rec30DetailsAmalagationMerge",
                    "heading": "Type of Entity",
                    "subHead": "",
                    "width": "8%"
                }, {
                    "name": "relatOfAmlEntityWithLstEnt_Rec30DetailsAmalagationMerge",
                    "heading": "Relationship with listed entity(ies)",
                    "subHead": "",
                    "width": "10%"
                }, {
                    "name": "dtlsOfOthrRelatAmlEntLstEnt_Rec30DetailsAmalagationMerge",
                    "heading": "Details of other relations",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "preBbNumShUndrPPGCtgAmlOrME_Rec30DetailsAmalagationMerge",
                    "heading": "Number of shares",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "preBbPrctgShUndrPPGCtg_Rec30DetailsAmalagationMerge",
                    "heading": "Percentage",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "preBbNumOfShUndrPublicCtg_Rec30DetailsAmalagationMerge",
                    "heading": "Number of shares",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "preBbPrcntgeOfShUndrPblcCtg_Rec30DetailsAmalagationMerge",
                    "heading": "Percentage",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "preBbNumOfShUndrOtherCtg_Rec30DetailsAmalagationMerge",
                    "heading": "Number of shares",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "preBbPPrcntgeShUndrOthrCtg_Rec30DetailsAmalagationMerge",
                    "heading": "Percentage",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "preBbTtlNumOfShares_Rec30DetailsAmalagationMerge",
                    "heading": "Number of shares",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "preBbTtlPPrcntgeOfShares_Rec30DetailsAmalagationMerge",
                    "heading": "Percentage",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "postBbNumOfShUndrPPGCtg_Rec30DetailsAmalagationMerge",
                    "heading": "Number of shares",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "postBbPrctgOfShUndrPPGCtg_Rec30DetailsAmalagationMerge",
                    "heading": "Percentage",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "postBbNumOfShUndrPublicCtg_Rec30DetailsAmalagationMerge",
                    "heading": "Number of shares",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "postBbPrcntgShUndrPublicCtg_Rec30DetailsAmalagationMerge",
                    "heading": "Percentage",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "postBbNumOfShUndrOtherCtg_Rec30DetailsAmalagationMerge",
                    "heading": "Number of shares",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "postBbPrcntgeShUndrOtherCtg_Rec30DetailsAmalagationMerge",
                    "heading": "Percentage",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "postBbTotalNumberOfShares_Rec30DetailsAmalagationMerge",
                    "heading": "Number of shares",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "postBbTotalPrcntgeOfShares_Rec30DetailsAmalagationMerge",
                    "heading": "Percentage",
                    "subHead": "",
                    "width": ""
                }];
            } else if (containerId === "RecUnitEventSlumpSale") {
                rowsData = rowsData.map(function (row) {
                    return row.filter(function (cell) {
                        return cell.text !== "Type of Entity";
                    });
                });
                tableColumnData = [{
                    "name": "nameOfRestructEnt_Rec130DetailsEvtOthrRestrctring",
                    "heading": "Name of the Entity",
                    "subHead": "",
                    "width": "10%"
                }, {
                    "name": "restrctEntRltnEntListEnt_Rec130DetailsEvtOthrRestrctring",
                    "heading": "Relationship with listed entity(ies)",
                    "subHead": "",
                    "width": "10%"
                }, {
                    "name": "dtlsOthrRltnRestructEntListEnt_Rec130DetailsEvtOthrRestrctring",
                    "heading": "Details of other relations",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "preBBNumShrPrmtrOthrRestruct_Rec130DetailsEvtOthrRestrctring",
                    "heading": "Number of shares",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "preBBPercShrPrmtrOthrRestruct_Rec130DetailsEvtOthrRestrctring",
                    "heading": "Percentage",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "preBBNumShrPblcOthrRestruct_Rec130DetailsEvtOthrRestrctring",
                    "heading": "Number of shares",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "preBBPercShrPblcOthrRestruct_Rec130DetailsEvtOthrRestrctring",
                    "heading": "Percentage",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "preBBNumShrOthrCatOthrRestruct_Rec130DetailsEvtOthrRestrctring",
                    "heading": "Number of shares",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "preBBPerShrOthrCatOthrRestruct_Rec130DetailsEvtOthrRestrctring",
                    "heading": "Percentage",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "preBBTtlNumShrOthrRestruct_Rec130DetailsEvtOthrRestrctring",
                    "heading": "Number of shares",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "preBBTtlPerShrOthrRestruct_Rec130DetailsEvtOthrRestrctring",
                    "heading": "Percentage",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "postBBNumShrPrmtrOthrRestruct_Rec130DetailsEvtOthrRestrctring",
                    "heading": "Number of shares",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "postBBPercShrPrmtrOthrRestruct_Rec130DetailsEvtOthrRestrctring",
                    "heading": "Percentage",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "postBBNumShrPblcOthrRestruct_Rec130DetailsEvtOthrRestrctring",
                    "heading": "Number of shares",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "postBBPercShrPblcOthrRestruct_Rec130DetailsEvtOthrRestrctring",
                    "heading": "Percentage",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "postBBNumShrOthrCatOthrRestrct_Rec130DetailsEvtOthrRestrctring",
                    "heading": "Number of shares",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "postBBPerShrOthrCatOthrRestrct_Rec130DetailsEvtOthrRestrctring",
                    "heading": "Percentage",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "postBBTtlNumOthrRestruct_Rec130DetailsEvtOthrRestrctring",
                    "heading": "Number of shares",
                    "subHead": "",
                    "width": ""
                }, {
                    "name": "postBBTtlPerShrOthrRestruct_Rec130DetailsEvtOthrRestrctring",
                    "heading": "Percentage",
                    "subHead": "",
                    "width": ""
                }];
            }
        } else if (containerId === "RecEventTypeDemerger") {
            dataJson = data[0].Rec50DetailsDemerger;
            tabletextContent = "Brief details of the division's to be Demerged";

            rowsData = [[{ text: "Name of Entity", rowspan: 3 }, { text: "Type of Entity", rowspan: 3 }, { text: "Relationship with listed entity(ies)", rowspan: 3 }, { text: "Details of other relations", rowspan: 3 }, { text: "Details of Pre Shareholding", colspan: 8 }, { text: "Details of Post Shareholding", colspan: 8 }], [{ text: "Promoter and Promoter Group", colspan: 2 }, { text: "Public", colspan: 2 }, { text: "Others", colspan: 2 }, { text: "Total", colspan: 2 }, { text: "Promoter and Promoter Group", colspan: 2 }, { text: "Public", colspan: 2 }, { text: "Others", colspan: 2 }, { text: "Total", colspan: 2 }], [{ text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }]];
            tableColumnData = [{
                "name": "nameDemergerEnt_Rec50DetailsDemerger",
                "heading": "Name of the Entity",
                "subHead": "",
                "width": "10%"
            }, {
                "name": "typeDemergerEnt_Rec50DetailsDemerger",
                "heading": "Type of Entity",
                "subHead": "",
                "width": "8%"
            }, {
                "name": "reltnDemergerEntWithListEnt_Rec50DetailsDemerger",
                "heading": "Relationship with listed entity(ies)",
                "subHead": "",
                "width": "10%"
            }, {
                "name": "dtlsOthReltnDemergerEntListEnt_Rec50DetailsDemerger",
                "heading": "Details of other relations",
                "subHead": "",
                "width": "6.66%"
            }, {
                "name": "preBBNumShrPrmtrDemerger_Rec50DetailsDemerger",
                "heading": "Percentage to the total turnover of the listed entity (filing this announcement) in the immediately preceding financial year/based on financials of  the last financial year",
                "subHead": "",
                "width": "6.66%"
            }, {
                "name": "preBBPercShrPrmtrDemerger_Rec50DetailsDemerger",
                "heading": "Number of shares",
                "subHead": "",
                "width": "6.66%"
            }, {
                "name": "preBBNumShrPblcDemerger_Rec50DetailsDemerger",
                "heading": "Percentage",
                "subHead": "",
                "width": "6.66%"
            }, {
                "name": "preBBPercShrPblcDemerger_Rec50DetailsDemerger",
                "heading": "Percentage",
                "subHead": "Public",
                "width": "6.66%"
            }, {
                "name": "preBBNumShrOthrCatDemerger_Rec50DetailsDemerger",
                "heading": "Number of shares",
                "subHead": "Others",
                "width": "6.66%"
            }, {
                "name": "preBBPerShrOthrCatDemerger_Rec50DetailsDemerger",
                "heading": "Percentage",
                "subHead": "Others",
                "width": "6.66%"
            }, {
                "name": "preBBTtlNumShrDemerger_Rec50DetailsDemerger",
                "heading": "Number of shares",
                "subHead": "Total",
                "width": "6.66%"
            }, {
                "name": "preBBTtlPerShrDemerger_Rec50DetailsDemerger",
                "heading": "Percentage",
                "subHead": "Total",
                "width": "6.66%"
            }, {
                "name": "postBBNumShrPrmtrDemerger_Rec50DetailsDemerger",
                "heading": "Number of shares",
                "subHead": "Promoter and Promoter Group",
                "width": "6.66%"
            }, {
                "name": "postBBPercShrPrmtrDemerger_Rec50DetailsDemerger",
                "heading": "Percentage",
                "subHead": "Promoter and Promoter Group",
                "width": "6.66%"
            }, {
                "name": "postBBNumShrPblcDemerger_Rec50DetailsDemerger",
                "heading": "Number of shares",
                "subHead": "Public",
                "width": "6.66%"
            }, {
                "name": "postBBPercShrPblcDemerger_Rec50DetailsDemerger",
                "heading": "Percentage",
                "subHead": "Public",
                "width": "6.66%"
            }, {
                "name": "postBBNumShrOthrCatDemerger_Rec50DetailsDemerger",
                "heading": "Number of shares",
                "subHead": "Others",
                "width": "6.66%"
            }, {
                "name": "postBBPerShrOthrCatDemerger_Rec50DetailsDemerger",
                "heading": "Percentage",
                "subHead": "Others",
                "width": "6.66%"
            }, {
                "name": "postBBTtlNumShrDemerger_Rec50DetailsDemerger",
                "heading": "Number of shares",
                "subHead": "Total",
                "width": "6.66%"
            }, {
                "name": "postBBTtlPerShrDemerger_Rec50DetailsDemerger",
                "heading": "Percentage",
                "subHead": "Total",
                "width": "6.66%"
            }];
        } else if (containerId === "RecSalesdisposal") {
            dataJson = data[0].Rec80TypeSalesdisposal;
            tabletextContent = "";

            rowsData = [[{ text: "Details of Unit/Division/Subsidiary", rowspan: 3 }, { text: "Type", rowspan: 3 }, { text: "Name of unit or division or Subsidiary of the listed entity", rowspan: 3 }, { text: "During the last financial year", colspan: 8 }], [{ text: "Turnover", colspan: 2 }, { text: "Revenue", colspan: 2 }, { text: "Income", colspan: 2 }, { text: "NetWorth", colspan: 2 }], [{ text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }]];
            tableColumnData = [{
                "name": "dtlsSaleOrDispslListEnt_Rec80TypeSalesdisposal",
                "heading": "Details of Unit/Division/Subsidiary"
            }, {
                "name": "typeSaleOrDispslListEnt_Rec80TypeSalesdisposal",
                "heading": "Type"
            }, {
                "name": "nameSaleOrDispslListEnt_Rec80TypeSalesdisposal",
                "heading": "Name of unit or division or Subsidiary of the listed entity"
            }, {
                "name": "prvsTurnOverSaleOrDispsListEnt_Rec80TypeSalesdisposal",
                "heading": "Number of shares"
            }, {
                "name": "prvsPercTrnOverSalDispsListEnt_Rec80TypeSalesdisposal",
                "heading": "Percentage to the total turnover of the listed entity (filing this announcement) in the immediately preceding financial year/based on financials of the last financial year"
            }, {
                "name": "prvsRevenuenSaleDispslListEnt_Rec80TypeSalesdisposal",
                "heading": "Number of shares"
            }, {
                "name": "revenuePercentage_Rec80TypeSalesdisposal",
                "heading": "Percentage"
            }, {
                "name": "prvsIncomOfSaleOrDispslListEnt_Rec80TypeSalesdisposal",
                "heading": "Percentage"
            }, {
                "name": "prvsPercIncmSaleDispslListEnt_Rec80TypeSalesdisposal",
                "heading": "Number of shares"
            }, {
                "name": "prvsNtWrthSaleOrDispslListEnt_Rec80TypeSalesdisposal",
                "heading": "Percentage"
            }, {
                "name": "networthPercentage_Rec80TypeSalesdisposal",
                "heading": "Number of shares"
            }];
        } else if (containerId === "RecEventSlumpSale") {
            dataJson = data[0].Rec110UnitEventSlumpSale;
            tabletextContent = "";

            rowsData = [[{ text: "Name of unit or division or Subsidiary of the listed entity", rowspan: 3, id: "nameOfSlumpSale_Rec110UnitEventSlumpSale" }, { text: "Type", rowspan: 3, id: "typeSaleOrDispslListEnt_Rec80TypeSalesdisposal" }, { text: "Area of business of the slump sale entity(ies)", rowspan: 3, id: "nameSaleOrDispslListEnt_Rec80TypeSalesdisposal" }, { text: "During the last financial year", colspan: 8 }, { text: "Details of Pre Shareholding", colspan: 8 }, { text: "Details of Post Shareholding", colspan: 8 }], [{ text: "Turnover", colspan: 2 }, { text: "Revenue", colspan: 2 }, { text: "Income", colspan: 2 }, { text: "NetWorth", colspan: 2 }, { text: "Promoter and Promoter Group", colspan: 2 }, { text: "Public", colspan: 2 }, { text: "Others", colspan: 2 }, { text: "Total", colspan: 2 }, { text: "Promoter and Promoter Group", colspan: 2 }, { text: "Public", colspan: 2 }, { text: "Others", colspan: 2 }, { text: "Total", colspan: 2 }], [{ text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }, { text: 'Number of shares' }, { text: 'Percentage' }]];
            tableColumnData = [{
                "name": "nameOfSlumpSale_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "",
                "width": "10%"
            }, {
                "name": "typeOfSlumpSale_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "",
                "width": "8%"
            }, {
                "name": "areaOfSaleEntities_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "",
                "width": "10%"
            }, {
                "name": "prvsTurnOverOfSlmpListEnt_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "",
                "width": "6.66%"
            }, {
                "name": "prvsPercTrnOverOfSlmpListEnt_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "",
                "width": "6.66%"
            }, {
                "name": "prvsRevenuenSlmpListEnt_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "",
                "width": "6.66%"
            }, {
                "name": "prvsPercRevenTrnOverSlmpList_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "",
                "width": "6.66%"
            }, {
                "name": "prvsIncomOfSlmpListEnt_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "Public",
                "width": "6.66%"
            }, {
                "name": "prvsPercIncmOfSlmpListEnt_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "Others",
                "width": "6.66%"
            }, {
                "name": "prvsPercNtWrthOfSlmpListEnt_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "Others",
                "width": "6.66%"
            }, {
                "name": "dtlsPreBBSharPatFrSlmpEvnt_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "Total",
                "width": "6.66%"
            }, {
                "name": "preBBNumShrPrmtrSlmpSaleEvnt_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "Total",
                "width": "6.66%"
            }, {
                "name": "preBBPercShrPrmtrSlmpSaleEvnt_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "Total",
                "width": "6.66%"
            }, {
                "name": "preBBNumShrPblcSlmpSaleEvnt_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "Public",
                "width": "6.66%"
            }, {
                "name": "preBBPercShrPblcSlmpSaleEvnt_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "Public",
                "width": "6.66%"
            }, {
                "name": "preBBNumShrOthrCatSlmpSaleEvnt_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "Other Categories",
                "width": "6.66%"
            }, {
                "name": "preBBPerShrOthrCatSlmpSaleEvnt_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "",
                "width": "6.66%"
            }, {
                "name": "preBBTtlNumShrSaleEvnt_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "",
                "width": "6.66%"
            }, {
                "name": "preBBTtlPerShrSaleEvnt_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "",
                "width": "6.66%"
            }, {
                "name": "postBBNumShrPrmtrSlmpSaleEvnt_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "",
                "width": "6.66%"
            }, {
                "name": "postBBPercShrPrmtrSlmpSaleEvnt_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "",
                "width": "6.66%"
            }, {
                "name": "postBBNumShrPblcSlmpSaleEvnt_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "",
                "width": "6.66%"
            }, {
                "name": "postBBPercShrPblcSlmpSaleEvnt_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "",
                "width": "6.66%"
            }, {
                "name": "postBBNumShrOthrCatSlmpEvn_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "",
                "width": "6.66%"
            }, {
                "name": "postBBPerShrOthrCatSlmpEvn_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "",
                "width": "6.66%"
            }, {
                "name": "postBBTtlNumSlmpSaleEvnt_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "",
                "width": "6.66%"
            }, {
                "name": "postBBTtlPerShrSlmpSaleEvnt_Rec110UnitEventSlumpSale",
                "heading": "",
                "subHead": "",
                "width": "6.66%"
            }];
        } else if (containerId === "Rec30SubsequentDisclosure") {
            dataJson = data;
            tabletextContent = "";

            rowsData = [[{ text: "Type of Resolution" }, { text: "Heading of Resolution/Agenda	" }, { text: "Brief Details of resolution" }]];
            tableColumnData = [{
                "name": "nameOfResolutionAgda_Rec30SubsequentDisclosure",
                "heading": "",
                "subHead": "",
                "width": "10%"
            }, {
                "name": "typeOfResolution_Rec30SubsequentDisclosure",
                "heading": "",
                "subHead": "",
                "width": "8%"
            }, {
                "name": "categoryOfResolution_Rec30SubsequentDisclosure",
                "heading": "",
                "subHead": "",
                "width": "10%"
            }];
        } else if (containerId === "XbrlRecExeAgr") {
            dataJson = data[0].XbrlRec30Response;
            tabletextContent = "";

            rowsData = [[{ text: "Sr.No." }, { text: "Name(s) of parties with whom the agreement is entered" }, { text: "Shareholding, if any, in the entity with whom the agreement is executed" }, { text: "Number of Shares" }, { text: "Percentage of shareholding" }, { text: "Whether, the parties to the Agreement are related to promoter / promoter group / associate / holding / subsidiary / group companies / Director / KMP and its relatives in any manner." }, { text: "Nature of relationship" }]];
            tableColumnData = [{
                "name": "sr_no",
                "heading": "",
                "subHead": "",
                "width": "5%"
            }, {
                "name": "APE_NAME_PARTIES_XbrlRec30Response",
                "heading": "",
                "subHead": "",
                "width": "10%"
            }, {
                "name": "APE_SHAREHOLDING_XbrlRec30Response",
                "heading": "",
                "subHead": "",
                "width": "8%"
            }, {
                "name": "APE_NO_SHARE_XbrlRec30Response",
                "heading": "",
                "subHead": "",
                "width": "10%"
            }, {
                "name": "APE_PERC_SHAREHOLD_XbrlRec30Response",
                "heading": "",
                "subHead": "",
                "width": "10%"
            }, {
                "name": "APE_PRTIES_AGRMNT_XbrlRec30Response",
                "heading": "",
                "subHead": "",
                "width": "10%"
            }, {
                "name": "APE_NATURE_RELATION_XbrlRec30Response",
                "heading": "",
                "subHead": "",
                "width": "10%"
            }];
        }

        var heading = document.createElement("h4");
        heading.classList.add("section-heading");
        heading.textContent = tabletextContent;

        // Create the wrapping <div> elements
        var divWrap1 = document.createElement("div");
        divWrap1.classList.add("table-wrap", "maxHeight-900", "scrollWrap", "custom-scrollbar");

        var tablerow = document.createElement("table");
        tablerow.setAttribute("id", "table-tableData");
        tablerow.classList.add("common_table", "customHeight-table", "table", "table-bordered", "tableScroll", "mb-0");

        // Creating the thead element
        var _thead = document.createElement("thead");

        // Iterate over the rows data
        rowsData.forEach(function (rowData) {
            // Creating the <tr> element
            var tr = document.createElement("tr");

            // Iterate over the cells data in the current row
            rowData.forEach(function (cellData) {
                // Creating and appending the <th> element with attributes and text content
                var th = document.createElement("th");
                Object.keys(cellData).forEach(function (attr) {
                    th.setAttribute(attr, cellData[attr]);
                });
                th.textContent = cellData.text;
                // th.classList.add("text-center");
                tr.appendChild(th);
            });

            // Appending the <tr> to the <thead> element
            _thead.appendChild(tr);
        });

        // Appending the <thead> to the <table> element
        tablerow.appendChild(_thead);
        divWrap1.appendChild(tablerow);

        tableContainer.appendChild(heading);
        tableContainer.appendChild(divWrap1);

        var tableData = customTableNoHead({
            tableStyle: {
                id: "",
                class: ""
            },
            colData: tableColumnData || [],
            rowData: []
        });
        B.render(tableData, B.findOne("#table-tableData"));
        B.findOne("#table-tableData .emptyRow").innerHTML = loader;
        var dataArrayWithSrNo = dataJson.map(function (obj, index) {
            return _extends({}, obj, { sr_no: index + 1 });
        });
        tableData.state.rowData = dataArrayWithSrNo || [];
    }
    if (containerId != "Rec30SubsequentDisclosure") {
        var _table = document.createElement("table");
        _table.classList.add("common_table", "customHeight-table", "table", "table-bordered", "jsonTable", "mt-2");

        var tableBody = document.createElement("tbody");

        for (var i = 0; i < data.length; i++) {
            var newJsonData = void 0;
            if (containerId === 'AllotmentOfSecRecord60') {
                newJsonData = _extends({}, data[i]);
                delete newJsonData.rmkExchNotWDAllotSec_AllotmentOfSecRecord60;
            } else if (containerId === 'RestrictionOfSecRecord50') {
                newJsonData = _extends({}, data[i]);
                delete newJsonData.remarksExchNotWDForRestOnTrans_RestrictionOfSecRecord50;
            } else if (containerId === 'AlterationOfExistSecRecord40') {
                newJsonData = _extends({}, data[i]);
                delete newJsonData.rmkForExchNotForWDForAltTS_AlterationOfExistSecRecord40;
            } else if (containerId === 'IssuanceOfSecuritiesRecord20') {
                newJsonData = _extends({}, data[i]);
                delete newJsonData.exchNotWebsiteDissRemarksIos_IssuanceOfSecuritiesRecord20;
            } else if (containerId === 'AlterationOfCapitalRecord30') {
                newJsonData = _extends({}, data[i]);
                delete newJsonData.rmkForExchNotForWDForAltOfCap_AlterationOfCapitalRecord30;
            } else if (containerId === "Rec30BuyBAck") {
                newJsonData = _extends({}, data[i]);
                delete newJsonData.preBBShareUnderPromoterCat_Rec30BuyBAck;
                delete newJsonData.preBBShareUnderPublicCat_Rec30BuyBAck;
                delete newJsonData.preBBShareUnderOtherCat_Rec30BuyBAck;
                delete newJsonData.preBBNoOfShares_Rec30BuyBAck;
                delete newJsonData.preBBPromotShrCapitalPrcnt_Rec30BuyBAck;
                delete newJsonData.preBBPublicShrCapitalPrcnt_Rec30BuyBAck;
                delete newJsonData.preBBOtherShareCapitalPrcnt_Rec30BuyBAck;
                delete newJsonData.preBBTotalShrCapitalPrcnt_Rec30BuyBAck;
                delete newJsonData.whetherPostBBPatternAvlble_Rec30BuyBAck;
                delete newJsonData.ntsUnavlbltyOfPostBBDtls_Rec30BuyBAck;
                delete newJsonData.postBBShareUnderPromoterCat_Rec30BuyBAck;
                delete newJsonData.postBBShareUnderPublicCat_Rec30BuyBAck;
                delete newJsonData.postBBShareUnderOtherCat_Rec30BuyBAck;
                delete newJsonData.postBBNoOfShares_Rec30BuyBAck;
                delete newJsonData.postBBPromotShrCapitalPrcnt_Rec30BuyBAck;
                delete newJsonData.postBBPublicShrCapitalPrcnt_Rec30BuyBAck;
                delete newJsonData.postBBOtherShareCapitalPrcnt_Rec30BuyBAck;
                delete newJsonData.postBBTotShareCapitalPrcnt_Rec30BuyBAck;
            } else if (containerId === "RecDetailsAmalagation") {
                newJsonData = data[i].Rec20EventAmalagationMerge[0];
            } else if (containerId === "RecEventTypeDemerger") {
                newJsonData = data[i].Rec40EventTypeDemerger[0];
            } else if (containerId === "RecSalesdisposal") {
                newJsonData = data[i].Rec70EventTypeSalesdisposal[0];
            } else if (containerId === "RecEventSlumpSale") {
                newJsonData = data[i].Rec100EventSlumpSale[0];
            } else if (containerId == "Rec60EventTypeAcquistion") {
                newJsonData = _extends({}, data[i]);
                delete newJsonData.startYearFirstPrev_Rec60EventTypeAcquistion;
                delete newJsonData.endYearFirstPrev_Rec60EventTypeAcquistion;
                delete newJsonData.turnoverFirstPrev_Rec60EventTypeAcquistion;
                delete newJsonData.startsecondPrevYear_Rec60EventTypeAcquistion;
                delete newJsonData.endsecondPrevYear_Rec60EventTypeAcquistion;
                delete newJsonData.secondPrevTurnover_Rec60EventTypeAcquistion;
                delete newJsonData.startthirdPrevYear_Rec60EventTypeAcquistion;
                delete newJsonData.endthirdPrevYear_Rec60EventTypeAcquistion;
                delete newJsonData.thirdPrevTurnover_Rec60EventTypeAcquistion;
                delete newJsonData.countryAcqrdPresence_Rec60EventTypeAcquistion;
                delete newJsonData.anyOthrBrfSignfInfoAcquston_Rec60EventTypeAcquistion;
            } else if (containerId == "RecUnitEventSlumpSale") {
                newJsonData = data[i].Rec120EventOtherRestructuring[0];
            } else if (containerId === "Rec30SubsequentDisclosure") {
                newJsonData = data[i].Rec30SubsequentDisclosure[0];
            } else if (containerId === "XbrlRecExeAgr") {
                newJsonData = data[i].XbrlRec20Response[0];
            } else {
                newJsonData = data[i];
            }

            if (containerId === 'AllotmentOfSecRecord60') {
                addRowToTable(tableBody, "Date of Board meeting for approval of issuance of security", newJsonData["dtBMApprIssAllotSec_AllotmentOfSecRecord60"]);
                addRowToTable(tableBody, "Whether any disclosure was made for the issuance of securities as per SEBI LODR and SEBI Circular September 09, 2015", newJsonData["whDisMadeSEBIAllotSec_AllotmentOfSecRecord60"]);
                addRowToTable(tableBody, "If Yes, specify the date of disclosure", newJsonData["dtsDisMadeSEBIAllotSec_AllotmentOfSecRecord60"]);
                addRowToTable(tableBody, "If No, provide reason for non-disclosure", newJsonData["resonNonDisSEBIAllotSec_AllotmentOfSecRecord60"]);
                addRowToTable(tableBody, "Date of Board / Committee for Allotment of Securities", newJsonData["dtBoardCommitteeAllotSec_AllotmentOfSecRecord60"]);
                addRowToTable(tableBody, "Type of Securities Allotted", newJsonData["typeSecAllotAllotSec_AllotmentOfSecRecord60"]);
                addRowToTable(tableBody, "If Others, please specify", newJsonData["detlsOtherSecAllotSec_AllotmentOfSecRecord60"]);
                addRowToTable(tableBody, "Type of Issuance", newJsonData["typeIssAllotSec_AllotmentOfSecRecord60"]);
                addRowToTable(tableBody, "If Any other method, please specify", newJsonData["otherMethodAllotSec_AllotmentOfSecRecord60"]);
                // Create "Pre - Allotment of Securities" label and rows
                addLabelRowToTable(tableBody, "Pre - Allotment of Securities");
                addRowToTable(tableBody, "Paid-up share capital", newJsonData["pdUpShCapPreAllotSec_AllotmentOfSecRecord60"]);
                addRowToTable(tableBody, "Number of Shares", newJsonData["numSharesPaidUpPreAllotSec_AllotmentOfSecRecord60"]);
                // Create "Post - Allotment of Securities" label and rows
                addLabelRowToTable(tableBody, "Post - Allotment of Securities");
                addRowToTable(tableBody, "Paid-up share capital", newJsonData["pdUpShCapPostAllotSec_AllotmentOfSecRecord60"]);
                addRowToTable(tableBody, "Number of Shares", newJsonData["numSharesPaidUpPostAllotSec_AllotmentOfSecRecord60"]);
                addRowToTable(tableBody, "Post allotment of securities - outcome of the subscription", newJsonData["outcomeSubPostAllotSec_AllotmentOfSecRecord60"]);
                addRowToTable(tableBody, "Issue price / allotted price", newJsonData["issuePriceAllotSec_AllotmentOfSecRecord60"]);
                addRowToTable(tableBody, "Number of investors", newJsonData["numInvestAllotSec_AllotmentOfSecRecord60"]);
                addRowToTable(tableBody, "Any other disclosure w.r.t. compliance of any SEBI Act, Regulation, Circular or provision", newJsonData["anyOtherDisSEBIRegAllotSec_AllotmentOfSecRecord60"]);
                addRowToTable(tableBody, "Any other information", newJsonData["anyOtherInfAllotSec_AllotmentOfSecRecord60"]);
                addRowToTable(tableBody, "Remarks", newJsonData["rmkWDAllotSec_AllotmentOfSecRecord60"]);
            } else if (containerId === 'AlterationOfCapitalRecord30') {
                addRowToTable(tableBody, 'Date of  of Board Meeting considering decision on any alteration of capital, including callsoard Meeting considering the decision with respect to fund raising', newJsonData['dtBMConsDecisionAltCapInCall_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Meeting Commencement Time', newJsonData['metingComntTimeAltOfCap_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Whether prior intimation of board meeting considering the alteration given to stock exchange', newJsonData['piofBMConsAltGivenToSEAltOfCap_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Date of prior intimation of board meeting considering alteration submitted to stock exchange', newJsonData['dtOfPIOfBMConsAltSubmittedToSE_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'If No, provide reason for non-disclosure', newJsonData['rsonForNonDisclosrIntimation_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Whether consideration for decision on any alteration of capital, including calls approved / recommended by the Board', newJsonData['consForDecisionAltOfCapIsAprd_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'If No or Deferred, please provide reason', newJsonData['rsonForConsDeciOnAnyAltCap_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Whether the board discussed on the agenda item prior to deferring the decision on alteration of capital, including calls', newJsonData['bodDisAgnItemPirDefTheDeciAlt_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'If Yes, provide details of the discussion', newJsonData['detailsOfTheBodDisOnTheAgnItem_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Whether Date of AGM / EGM / Postal Ballot/ Others is fixed', newJsonData['dtOfAoEoPBOrOthersIsFixForAlt_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Date of AGM / EGM / Postal Ballot /Others', newJsonData['dtOfAoEoPBOrOthersForAltOfCap_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'If No, provide reason', newJsonData['rsonForDtOfAoEoPBOrOtherNotFix_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Whether Record / Book closure date fixed by the company', newJsonData['whrRecOrBokCloDtFixByTheCom_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'If No, provide reason', newJsonData['rsonForRecBokCloDtNotFixByCom_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Record / Book Closure date', newJsonData['recDtOrBokCloDtForAltOfCap_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Record Date', newJsonData['recDtForAltOfCap_AlterationOfCapitalRecord30']);

                addLabelRowToTable(tableBody, "Book Closure");
                addRowToTable(tableBody, 'Start Date Of Book Closure Date', newJsonData['startDtOfBokCloDtOfAltOfCap_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'End Date Of Book Closure Date', newJsonData['endDtOfBokCloDtOfAltOfCap_AlterationOfCapitalRecord30']);

                addLabelRowToTable(tableBody, "Increase in Authorized Share Capital");
                addRowToTable(tableBody, 'Type of Shares', newJsonData['typeOfShr_AlterationOfCapitalRecord30']);

                addLabelRowToTable(tableBody, "Existing Authorised Share Capital");
                addRowToTable(tableBody, 'Number of Shares', newJsonData['numOfExistShrAuth_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Face Value of Shares', newJsonData['faceValueOfExistShrAuth_AlterationOfCapitalRecord30']);

                addLabelRowToTable(tableBody, "Proposed Authorized share capital");
                addRowToTable(tableBody, 'Number of Shares', newJsonData['numOfProposedShrAuth_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Face Value of Shares', newJsonData['faceValueOfProposedShrAuth_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Rationale for increase', newJsonData['rationaleForIncAuthShrCap_AlterationOfCapitalRecord30']);

                addLabelRowToTable(tableBody, "Split/Consolidation of Shares");
                addRowToTable(tableBody, 'Type of Event', newJsonData['typeSplitOrCnsldtionOfShrEvent_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Class of shares which are consolidated or split', newJsonData['classOfShrWhichSplitCnsldtion_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Split/Consolidation ratio', newJsonData['ratioOfSplitOrCnsldtion_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Rationale behind split/consolidation', newJsonData['rationaleForSplitOrCnsldtion_AlterationOfCapitalRecord30']);

                addLabelRowToTable(tableBody, "Pre-Share Capital");
                addRowToTable(tableBody, 'Authorised Share Capital', newJsonData['authShrCapPreSplitOrCnsldtion_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Subscribed Share Capital', newJsonData['subscrbShrCapPreSplitCnsldtion_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Paid-up Share Capital', newJsonData['paidUpShrCapPreSplitCnsldtion_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Face value of shares', newJsonData['faceValuePreSplitOrCnsldtion_AlterationOfCapitalRecord30']);

                addLabelRowToTable(tableBody, "Post-Share Capital");
                addRowToTable(tableBody, 'Authorised Share Capital', newJsonData['authShrCapPostSplitOrCnsldtion_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Subscribed Share Capital', newJsonData['subscrdShrCapPostSpltCnsldtion_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Paid-up Share Capital', newJsonData['paidUpShrCapPostSplitCnsldtion_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Face value of shares', newJsonData['faceValuePostSplitOrCnsldtion_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Expected time of completion', newJsonData['expTimeCompOfSplitOrCnsldtion_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Whether the proposed consolidation results in changes in voting percentage of shareholders', newJsonData['proCnsldtionResInChngInVPeOfSH_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Number of shares of each class pre split or consolidation', newJsonData['numShrEchClsPreSplitCnsldtion_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Number of shares of each class post split or consolidation', newJsonData['numShrEchClsPostSplitCnsldtion_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Number of shareholders who did not get any shares in consolidation or split and their pre-consolidation or or split shareholding', newJsonData['numOfSHNotGetShrInSptOrCnsl_AlterationOfCapitalRecord30']);

                addLabelRowToTable(tableBody, "Conversion of Share Capital");
                addRowToTable(tableBody, 'Types of Conversion', newJsonData['typesOfConversionOfShrCap_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Brief Particulars of Conversion of Share Capital', newJsonData['particularofConversionOfShrCap_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Rationale behind Conversion of Share Capital', newJsonData['rationaleForConversionOfShrCap_AlterationOfCapitalRecord30']);

                addLabelRowToTable(tableBody, "Pre - Conversion of Share Capital");
                addRowToTable(tableBody, 'Paid-up Share Capital', newJsonData['paidUpShrCapPreConversonShrCap_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Number of Shares', newJsonData['numShrPaidUpPreConversonShrCap_AlterationOfCapitalRecord30']);

                addLabelRowToTable(tableBody, "Post - Conversion of Share Capital");
                addRowToTable(tableBody, 'Paid-up Share Capital', newJsonData['paidUpShrCapPstConversinShrCap_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Number of Shares', newJsonData['numShrPaidUpPostConvertShrCap_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Whether Conversion of Share Capital is under the Scheme of arrangement and amalgamation under Section 230 to 232 of the Companies Act, 2013.', newJsonData['covrnOfShrCapIsUnTheSchemeAAA_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Date of NCLT order', newJsonData['dtOfNCLTOrder_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Date of Execution of Loan Agreement', newJsonData['dtOfExecutionOfLoanAgreement_AlterationOfCapitalRecord30']);

                addLabelRowToTable(tableBody, "Sub-Division of Shares");
                addRowToTable(tableBody, 'Class of shares which are subdivided', newJsonData['classOfShrWhichAreSubDivided_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Ratio of Sub-division', newJsonData['ratioOfSubDivision_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Rationale for Sub-division', newJsonData['rationaleForSubDivision_AlterationOfCapitalRecord30']);

                addLabelRowToTable(tableBody, "Pre - Share Capital");
                addRowToTable(tableBody, 'Authorised Share Capital', newJsonData['authShrCapPreSubDivision_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Subscribed Share Capital', newJsonData['subscribedShrCapPreSubDivision_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Paid-up Share Capital', newJsonData['paidUpShrCapPreSubDivision_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Face value of shares', newJsonData['faceValuePreSubDivision_AlterationOfCapitalRecord30']);

                addLabelRowToTable(tableBody, "Post - Share Capital");
                addRowToTable(tableBody, 'Authorised Share Capital', newJsonData['authShrCapPostSubDivision_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Subscribed Share Capital', newJsonData['subscribShrCapPostSubDivision_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Paid-up Share Capital', newJsonData['paidUpShrCapPostSubDivision_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Face value of shares', newJsonData['faceValuePostSubDivision_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Expected time of completion', newJsonData['expTimeCompletionOfSubDivision_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Number of shares of each class pre sub-division', newJsonData['numOfShrOfEchClsPreSubDivision_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Number of shares of each class post sub-division', newJsonData['numShrOfEchClsPostSubDivision_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Number of shareholders who did not get any shares in sub-division and their pre-subdivision shareholding.', newJsonData['numOfSHDidNotGetShrInSubDiv_AlterationOfCapitalRecord30']);

                addLabelRowToTable(tableBody, "Cancellation of Share Capital");
                addRowToTable(tableBody, 'Class of shares ', newJsonData['classOfShrCancelled_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'No. of shares proposed to be cancelled', newJsonData['numOfShrProposedToBeCancelled_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Face Value of Shares for cancellation', newJsonData['faceValueOfShrCancelled_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Rationale for cancellation of shares', newJsonData['rationaleForCancellationOfShr_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Brief Particulars of cancellation of shares', newJsonData['particularsOfCancellationOfShr_AlterationOfCapitalRecord30']);

                addLabelRowToTable(tableBody, "Pre - Shareholding");
                addRowToTable(tableBody, 'Paid-up Share Capital', newJsonData['paidUpShrCapPreCancelOfShr_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Number of Shares', newJsonData['numOfShrPaidUpPreCancelOfShr_AlterationOfCapitalRecord30']);

                addLabelRowToTable(tableBody, "Post - Shareholding");
                addRowToTable(tableBody, 'Paid-up Share Capital', newJsonData['paidUpShrCapPostCancelOfShr_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Number of Shares', newJsonData['numOfShrPaidUpPostCancelOfShr_AlterationOfCapitalRecord30']);

                addLabelRowToTable(tableBody, "Alteration of Share Capital, Including Calls");
                addRowToTable(tableBody, 'Rationale behind Alteration of share capital, including calls', newJsonData['rationaleForAltOfShrCapIndCals_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Brief Particulars of Alteration of share capital, including calls', newJsonData['particularsOfAltOfShrCapIndCal_AlterationOfCapitalRecord30']);

                addLabelRowToTable(tableBody, "Pre - Shareholding");
                addRowToTable(tableBody, 'Paid-up Share Capital', newJsonData['paidUpShrCapPreAltShrCapIndCal_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Number of Shares', newJsonData['numShrPaidUpPreAltShrCapIndCal_AlterationOfCapitalRecord30']);

                addLabelRowToTable(tableBody, "Post - Shareholding");
                addRowToTable(tableBody, 'Paid-up Share Capital', newJsonData['paidUpShrCapPstAltShrCapIndCal_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Number of Shares', newJsonData['shrPaidUpPostAltOfShrCapIndCal_AlterationOfCapitalRecord30']);

                addLabelRowToTable(tableBody, "Any Other Method");
                addRowToTable(tableBody, 'Method of Alteration of Capital', newJsonData['methodOfAltOfCap_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Brief Particulars of Alteration of Capital', newJsonData['particularsOfAltOfShrCap_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Rationale behind Alteration of Capital', newJsonData['rationaleForAltOfShrCap_AlterationOfCapitalRecord30']);

                addLabelRowToTable(tableBody, "Pre - Shareholding");
                addRowToTable(tableBody, 'Paid-up Share Capital', newJsonData['paidUpShrCapPreAlt_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Number of Shares', newJsonData['numOfShrPaidUpPreAlt_AlterationOfCapitalRecord30']);

                addLabelRowToTable(tableBody, "Post - Shareholding");
                addRowToTable(tableBody, 'Paid-up Share Capital', newJsonData['paidUpShrCapPostAlt_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Number of Shares', newJsonData['numOfShrPaidUpPostAlt_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Any other disclosure w.r.t. compliance of any SEBI Act, Regulation, Circular or provision', newJsonData['anOthrDiscRespectCompSEBIReg_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Any other information', newJsonData['anOthrInfoRelatedToAltOfCap_AlterationOfCapitalRecord30']);
                addRowToTable(tableBody, 'Remarks', newJsonData['rmkWDForAltOfCap_AlterationOfCapitalRecord30']);
            } else if (containerId === 'AlterationOfExistSecRecord40') {
                addRowToTable(tableBody, 'Date of Board Meeting considering the decision for alteration of the terms or structure of any existing securities', newJsonData['dtOfBMForAltOfExistSec_AlterationOfExistSecRecord40']);
                addRowToTable(tableBody, 'Meeting Commencement Time', newJsonData['meetingCommtTimeForAltOfTS_AlterationOfExistSecRecord40']);
                addRowToTable(tableBody, 'Meeting Conclusion Time', newJsonData['meetingConcluTimeForAltOfTS_AlterationOfExistSecRecord40']);
                addRowToTable(tableBody, 'Whether prior intimation of board meeting considering alteration given to stock exchange', newJsonData['intBMConsAltGivenToexchange_AlterationOfExistSecRecord40']);
                addRowToTable(tableBody, 'Date of prior intimation of board meeting considering alteration submitted to stock exchange', newJsonData['dtOfPrIntBMConAltSubToexchange_AlterationOfExistSecRecord40']);
                addRowToTable(tableBody, 'If No, provide reason for non-disclosure', newJsonData['rsonNonDsclIntOfBMCons_AlterationOfExistSecRecord40']);
                addRowToTable(tableBody, 'Whether decision on alteration approved by the Board', newJsonData['whrDeciOnAltApprByTheBoard_AlterationOfExistSecRecord40']);
                addRowToTable(tableBody, 'If No or Deferred, provide reason', newJsonData['rsonForDeciOnAltIsNotAprBord_AlterationOfExistSecRecord40']);
                addRowToTable(tableBody, 'Whether the Board discussed on the agenda item prior to deferring the proposal on alteration', newJsonData['bdiscusAgndItemPrToDefProOnAlt_AlterationOfExistSecRecord40']);
                addRowToTable(tableBody, 'If Yes, provide details of the discussion', newJsonData['detlsOfTheBDOnTheAgndItemPr_AlterationOfExistSecRecord40']);
                addRowToTable(tableBody, 'Type of Action which will result in alteration of the terms or structure of any existing securities', newJsonData['typeActAltOfTSOfAnyExistSec_AlterationOfExistSecRecord40']);
                addRowToTable(tableBody, 'Date on which such alteration of the terms or structure of any existing securities are effective', newJsonData['dtAltTSOfAnyExistSecAreEff_AlterationOfExistSecRecord40']);
                addRowToTable(tableBody, 'Details of such alteration of the terms or structure of any existing securities', newJsonData['detlsOfAltOfTheTSOfAnyExistSec_AlterationOfExistSecRecord40']);

                addLabelRowToTable(tableBody, "Pre - Issue");
                addRowToTable(tableBody, 'Paid-up Share Capital pre', newJsonData['paidUpShareCapitalPreAltOfTS_AlterationOfExistSecRecord40']);
                addRowToTable(tableBody, 'Number of Shares pre', newJsonData['numOfSharesPaidUpPreAltOfTS_AlterationOfExistSecRecord40']);

                addLabelRowToTable(tableBody, "Post - Issue");
                addRowToTable(tableBody, 'Paid-up Share Capital post', newJsonData['paidUpShareCapitalPostAltOfTS_AlterationOfExistSecRecord40']);
                addRowToTable(tableBody, 'Number of Shares post', newJsonData['numOfSharesPaidUpPostAltOfTS_AlterationOfExistSecRecord40']);
                addRowToTable(tableBody, 'Any other disclosure w.r.t. compliance of any SEBI Act, Regulation, Circular or provision', newJsonData['anyOtherDsclorWithResCompSEBI_AlterationOfExistSecRecord40']);
                addRowToTable(tableBody, 'Any other information', newJsonData['otherInformationRelatedtoalter_AlterationOfExistSecRecord40']);
                addRowToTable(tableBody, 'Remarks', newJsonData['rmkWDForAltOfTS_AlterationOfExistSecRecord40']);
            } else if (containerId === 'Rec30SubsequentCDR') {
                addRowToTable(tableBody, 'Stage of the implementation of the CDR scheme', newJsonData['stgOfimpOfCdrSch_Rec30SubsequentCDR']);
                addLabelRowToTable(tableBody, "Execution stage of the CDR Scheme");
                addRowToTable(tableBody, 'Date of execution of the agreement', newJsonData['dtOfExceOfAgree_Rec30SubsequentCDR']);
                addRowToTable(tableBody, 'Parties to the agreement', newJsonData['partiesToAgree_Rec30SubsequentCDR']);
                addRowToTable(tableBody, 'Principal terms of the agreement', newJsonData['prinTermOfAgree_Rec30SubsequentCDR']);
                addRowToTable(tableBody, 'Brief summary of the agreement Executed under Corporate Debt Restructuring Scheme', newJsonData['sumOfAgreeExceUndCdrSch_Rec30SubsequentCDR']);
                addLabelRowToTable(tableBody, "Other stage of the CDR Scheme");
                addRowToTable(tableBody, 'Details of other stage of CDR Scheme', newJsonData['dtlsOfOthStgCdrSch_Rec30SubsequentCDR']);
                addRowToTable(tableBody, 'Details of final CDR package as approved by RBI and the lenders', newJsonData['dtlsOfFinCdrPackAppByRbiLen_Rec30SubsequentCDR']);
                addRowToTable(tableBody, 'Details of Lenders involved in Corporate Debt Restructuring', newJsonData['dtlsOfLenInvolInCdr_Rec30SubsequentCDR']);
                addRowToTable(tableBody, 'Brief summary of the Corporate Debt Restructuring Scheme', newJsonData['sumOfCdrSch_Rec30SubsequentCDR']);
                addRowToTable(tableBody, 'Details of the securities involved in Corporate Debt Restructuring', newJsonData['dtlsOfSecInvolInCdr_Rec30SubsequentCDR']);
                addRowToTable(tableBody, 'Details of the interest payment and/or repayment schedule', newJsonData['dtlsOfIntPayAndRepaySch_Rec30SubsequentCDR']);
                addRowToTable(tableBody, 'Details of the negative and other restrictive covenants', newJsonData['dtlsOfNegAndOthResCov_Rec30SubsequentCDR']);
                addRowToTable(tableBody, 'Any other disclosure w.r.t. compliance of any SEBI Act, Regulation, Circular or provision', newJsonData['anyOthDisWrtComOfSebiRegCirProSub_Rec30SubsequentCDR']);
                addRowToTable(tableBody, 'Any other information', newJsonData['anyOthInfoSub_Rec30SubsequentCDR']);
                addRowToTable(tableBody, 'Remarks', newJsonData['websiteDissRemarksForSubsequent_Rec30SubsequentCDR']);
            } else if (containerId === 'IssuanceOfSecuritiesRecord20') {
                addRowToTable(tableBody, 'Whether the annoucement is submitted for any cancellation or termination of proposal for issuance of securities', newJsonData['annSubForCanOrTerProForIos_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Date of Board Meeting considering the decision with respect to cancellation or termination of proposal for issuance of securities', newJsonData['dtMeetConDecWithResToCancel_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Whether any disclosure is made for the issuance of securities as per SEBI Circular September 09, 2015', newJsonData['whthrDisMadForIosAsSebiSep_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'If Yes, please specify the date of disclsoure ', newJsonData['dtDisMadForIosAsSebiSep_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'If No, please provide reason for non-disclosure ', newJsonData['reaNonDisForIosAsSebiSep_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Reasons for cancellation or termination of proposal for issuance of securities', newJsonData['reaCanOrTerProForIos_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Date of Board Meeting considering the decision with respect to fund raising ', newJsonData['dtMeetConDecWithResToFr_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Meeting Commencement Time', newJsonData['meetComTimForIos_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Meeting Conclusion Time', newJsonData['meetConTimForIos_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Whether prior intimation of board meeting considering fund raising given to stock exchange', newJsonData['whthrPiOfMeetConFrToSe_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'If No, please provide reason for non-disclosure ', newJsonData['reaNonDisForPiMeetConFrToSe_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Date of prior intimation of board meeting considering fund raising submitted to stock exchange', newJsonData['dtOfPiMeetConFrSubToSe_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Whether decision on fund raising approved by the Board', newJsonData['whthrDecOnFrAppByBoard_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'If No or Deferred, please provide reason  ', newJsonData['reaDecOnFrNotAppOrDefByBoard_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Whether the Board discussed on the agenda item prior to defering the proposal on fund raising', newJsonData['whthrBoDisAipToDefProFr_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'If Yes, provide details of the discussion', newJsonData['dtlsBoDisAipToDefProFr_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Whether date of AGM / EGM / Postal Ballot/Other is fixed', newJsonData['whthrDtOfAoEoPBoOIsFIx_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'If No, please provide reason', newJsonData['reaDtOfAoEoPBoOIsNotFix_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Date of AGM / EGM / Postal Ballot/Other', newJsonData['dtOfAoEoPBoO_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Whether Record / Book closure date fixed by the company', newJsonData['whthrRecBookCloDtFix_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'If No, please provide reason', newJsonData['reaRecBookCloDtNotFix_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Record / Book Closure date', newJsonData['recBookCloDtForIos_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Record Date', newJsonData['recDtForIos_IssuanceOfSecuritiesRecord20']);

                addLabelRowToTable(tableBody, "Book Closure Date");
                addRowToTable(tableBody, 'Start Date Of Book Closure Date', newJsonData['stDtOfBookCloOfIos_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'End Date Of Book Closure Date', newJsonData['endDtOfBookCloOfIos_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Whether relevant date is set as per the provision of SEBI ICDR Regulations for determining the floor price', newJsonData['revDtSetAsSebiCdrRegForDfp_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'If No, please provide reason', newJsonData['reaRelDtIsNotSetAsSebiCdrReg_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Whether the Board decided the Mode through which fund shall be raised', newJsonData['whthrBoDecModThrWhiFunSbr_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'If No, please provide reason', newJsonData['reaBoNotDecModThrWhiFunSbr_IssuanceOfSecuritiesRecord20']);

                addLabelRowToTable(tableBody, "Further Public Offer");
                addRowToTable(tableBody, 'Type of securities proposed to be issued', newJsonData['typeOfSecProposedToBeIUFPO_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Total number of securities proposed to be issued', newJsonData['totalNumOfSecProposedToBeIUFPO_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Total amount for which the securities will be issued', newJsonData['totalAmtrWhichSecWillBeIUFPO_IssuanceOfSecuritiesRecord20']);

                addLabelRowToTable(tableBody, "Pre - Issue");
                addRowToTable(tableBody, 'Paid-up share capital', newJsonData['paidShCapPreFthrPubOff_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Number of Shares', newJsonData['numOfSharesPaidUpPreFthrPubOff_IssuanceOfSecuritiesRecord20']);

                addLabelRowToTable(tableBody, "Post - Issue");
                addRowToTable(tableBody, 'Paid-up share capital', newJsonData['paidShCapPostFthrPubOff_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Number of Shares', newJsonData['numOfShPaidUpPostFthrPubOff_IssuanceOfSecuritiesRecord20']);

                addLabelRowToTable(tableBody, "Right Issue");
                addRowToTable(tableBody, 'Type of securities proposed to be issued', newJsonData['typeOfSecProposedToBeIURI_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Total number of securities proposed to be issued', newJsonData['totalNumOfSecProposedToBeIURI_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Total amount for which the securities will be issued', newJsonData['totalAmtForWhichSecWillBeIURI_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Issue price', newJsonData['rightIssuePrice_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Ratio', newJsonData['rightIssueRatio_IssuanceOfSecuritiesRecord20']);

                addLabelRowToTable(tableBody, "Pre - Rights Issue");
                addRowToTable(tableBody, 'Paid-up share capital for Pre Right', newJsonData['paidShCapPreRightIssue_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Number of Shares for Pre Right', newJsonData['numOfSharesPaidUpPreRightIssue_IssuanceOfSecuritiesRecord20']);

                addLabelRowToTable(tableBody, "Post - Rights Issue");
                addRowToTable(tableBody, 'Paid-up share capital for Post Right', newJsonData['paidShCapPostRightIssue_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Number of Shares for Post Right', newJsonData['numOfSharePaidUpPostRightIssue_IssuanceOfSecuritiesRecord20']);

                addLabelRowToTable(tableBody, "Depository Receipts (ADR/GDR) or FCCB");
                addRowToTable(tableBody, 'Type of securities proposed to be issued', newJsonData['typeOfSecProBeIssueUnDeReFCCB_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Total number of securities proposed to be issued', newJsonData['numOfSecProToBeIssueUnDeReFCCB_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Total amount for which the securities will be issued', newJsonData['totalAmtTheSecIssueUnDeReFCCB_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Type of depository issued', newJsonData['typeOfDepositoryReceiptsAGF_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Name of the stock exchange where ADR/GDR/FCCBs are listed (opening – closing status) / proposed to be listed', newJsonData['nameOfTheSEAGFLstOrProBeListed_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Proposed Number of equity shares underlying the ADR / GDR or on conversion of FCCBs', newJsonData['numOfEquSharesProToBeUnder_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Proposed Date of allotment', newJsonData['proposedDateOfAllot_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Tenure', newJsonData['tenureOfDeposiReceiptsAGF_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Date of maturity', newJsonData['dateOfMatOfDeposiReceiptsAGF_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Issue price of ADR / GDR / FCCBs (in terms of USD)', newJsonData['issPriOfAdroGdroFccbUsd_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Issue price of ADR / GDR / FCCBs (in INR after considering conversion rate)', newJsonData['issPriOfAdroGdroFccbInr_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Details of Coupon offered, if any of FCCB’s', newJsonData['dtlsOfPayOfCoupOnFccb_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Change in terms of FCCBs, if any', newJsonData['chgInTermFccb_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Details of defaults, if any, by the listed entity in payment of coupon on FCCBs & subsequent updates in relation to the default, including the details of the corrective measures undertaken', newJsonData['detailDefaultsByListedEntity_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Actual date of payment of coupon on FCCBs', newJsonData['dtActPayOfCoupOnFccb_IssuanceOfSecuritiesRecord20']);

                addLabelRowToTable(tableBody, "Qualified Institutional Placement");
                addRowToTable(tableBody, 'Type of securities proposed to be issued', newJsonData['typSecProIssUndQualInstitPlace_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Total number of securities proposed to be issued', newJsonData['totNumSecIssUndQualInstitPlace_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Total amount for which the securities will be issued', newJsonData['totAmtWhiSecWillBeIssues_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Whether the company has already made Qualified Institutional Placements', newJsonData['comHasAlrMadeQualInstitPlace_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Date of previous Qualified Institutional Placements', newJsonData['dtOfPreQualInstitPlace_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Is QIB through offer for sale by promoters or promoters group for compliance with minimum public shareholding', newJsonData['whthrQibThruOffForSaleByPro_IssuanceOfSecuritiesRecord20']);

                addLabelRowToTable(tableBody, "Percentage of Public Shareholding");
                addRowToTable(tableBody, 'Pre - Percentage of Public Shareholding', newJsonData['perOfPreSh_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Post - Percentage of Public Shareholding', newJsonData['perOfPostSh_IssuanceOfSecuritiesRecord20']);

                addLabelRowToTable(tableBody, "Debt Securities or other non convertible securities");
                addRowToTable(tableBody, 'Type of securities proposed to be issued', newJsonData['typOfDeptSecOrOncSecIss_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Total number of securities proposed to be issued', newJsonData['totNumOfdeptSecOrOncSecIss_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Size of the issue', newJsonData['sizeOfDeptSecOrOncSec_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Whether proposed to be listed', newJsonData['whthrProToBeList_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'If Yes, name of the stock exchange', newJsonData['nmOfExgWhereDeptSecOrOncSec_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Tenure of the instrument', newJsonData['tenOfDeptSecOrOncSEC_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Date of allotment', newJsonData['diOfAlloOfDeptSecOrOncSec_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Date of maturity', newJsonData['dtOfMatOfDeptSecOrOncSec_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Particulars of coupon / interest offered', newJsonData['partOfCoupOrIntOff_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Schedule of payment of coupon / interest and principal', newJsonData['schOfPayOfCoupOrIp_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Details of Charge / security, if any, created over the assets', newJsonData['dtlsOfChgOrSecOfCrtOverAsset_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Particulars of special right / interest / privileges attached to the instrument and changes thereof', newJsonData['partOfSpeRigOrPriAttToInst_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Details of delay in payment of interest / principal amount for a period of more than three months from the due date or default in payment of interest / principal', newJsonData['dtlsOfDelForPerMorThanThrMon_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Details of any letter or comments regarding payment/non-payment of interest, principal on due dates, or any other matter concerning the security and /or the assets along with its comments thereon, if any', newJsonData['dtlsOfAoCRegPayOfIntOnDt_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Details of redemption of preference shares indicating the manner of redemption (whether out of profits or out of fresh issue) and debentures', newJsonData['dtlsRedPrefShrIndMannOfRedDeb_IssuanceOfSecuritiesRecord20']);

                addLabelRowToTable(tableBody, "Preferential Issue");
                addRowToTable(tableBody, 'Type of securities proposed to be issued', newJsonData['typSecProIssUndPrefIss_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Total number of securities proposed to be issued', newJsonData['totNumOfSecProIssUndPrefIss_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Total amount for which the securities will be issued', newJsonData['totAmtSecIssUndPrefIss_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Number of investors', newJsonData['numOfInvest_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Names of the investors', newJsonData['nmOfInvest_IssuanceOfSecuritiesRecord20']);

                addLabelRowToTable(tableBody, "Pre - Issue");
                addRowToTable(tableBody, 'Paid-up share capital pre preferential', newJsonData['paidScPrePrefIss_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Number of Shares pre pref preferential', newJsonData['numOfSpUpPrePrefIss_IssuanceOfSecuritiesRecord20']);

                addLabelRowToTable(tableBody, "Post - Issue");
                addRowToTable(tableBody, 'Paid-up share capital post preferential', newJsonData['paidScPostPrefIss_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Number of Shares post preferential', newJsonData['numOfSpUpPostPrefIss_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Outcome of the subscription post allotment ', newJsonData['outOfSubPostAllot_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Issue price / allotted price ', newJsonData['issPriOrAlloPriOfPreIss_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'In case of convertibles - intimation on conversion of securities or on lapse of the tenure of the instrument', newJsonData['intOnConOdSecOrLapOfTenOfInstr_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Date of conversion', newJsonData['dtOfConOfSecUpto_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Date of conversion of securities', newJsonData['dtOfConOfSec_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'In case of convertibles - Date on which the the tenure of the instrument lapsed', newJsonData['dtWhiTenOfInstLap_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Whether any change made in the date of conversion of securities', newJsonData['whthrChgMadInDtOfConSec_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Intimation of change in the Date of conversion of securities submitted to the Stock Exchange', newJsonData['dtIntChgDtConSecSubToExg_IssuanceOfSecuritiesRecord20']);

                addLabelRowToTable(tableBody, "Any Other Method");
                addRowToTable(tableBody, 'Type of securities proposed to be issued', newJsonData['typSecProIssUndOm_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Total number of securities proposed to be issued', newJsonData['totNumSecIssUndOm_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Total amount for which the securities will be issued', newJsonData['totAmtSecIssUndOm_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'name of the stock exchange where the securities are proposed to be listed', newJsonData['nmOfExWheProList_IssuanceOfSecuritiesRecord20']);

                addLabelRowToTable(tableBody, "Pre- Shareholding");
                addRowToTable(tableBody, 'Paid-up share capital pre shareholding', newJsonData['paidScPreIssue_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Number of Shares pre shareholding', newJsonData['numOfSpPreIssue_IssuanceOfSecuritiesRecord20']);

                addLabelRowToTable(tableBody, "Post- Shareholding");
                addRowToTable(tableBody, 'Paid-up share capital post shareholding', newJsonData['paidScPostIssue_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Number of Shares post shareholding', newJsonData['numOfSpPostIssue_IssuanceOfSecuritiesRecord20']);

                addRowToTable(tableBody, 'Any other disclosure w.r.t. compliance of any SEBI Act, Regulation, Circular or provision', newJsonData['anyOthDisWrtComOfSebiReg_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Any Other information', newJsonData['anyOthInfoRelToIos_IssuanceOfSecuritiesRecord20']);
                addRowToTable(tableBody, 'Remarks', newJsonData['websiteDissRemarksForIos_IssuanceOfSecuritiesRecord20']);
            } else if (containerId === 'Rec20BonusShare') {
                addRowToTable(tableBody, 'Types of Shares', newJsonData['typeOfShares_Rec20BonusShare']);
                addRowToTable(tableBody, 'Details of other type of securities', newJsonData['dtlSthrtType_Rec20BonusShare']);
                addRowToTable(tableBody, 'Date of Board Meeting where bonus recommended', newJsonData['bmDtWhereBonusRcmnded_Rec20BonusShare']);
                addRowToTable(tableBody, 'Meeting Commencement Time', newJsonData['bonusAnnBmStartTime_Rec20BonusShare']);
                addRowToTable(tableBody, 'Meeting Conclusion Time', newJsonData['bonusAnnBmEndTime_Rec20BonusShare']);
                addRowToTable(tableBody, 'Whether prior intimation of board meeting for recommending bonus filed with the Exchange', newJsonData['whthrBmCnsdrBonus_Rec20BonusShare']);
                addRowToTable(tableBody, 'Provide details if prior intimation of board meeting for recommending bonus not filed with the Exchange', newJsonData['ntsForBmNotCnsdrBonus_Rec20BonusShare']);
                addRowToTable(tableBody, 'Date of prior intimation of board meeting', newJsonData['bonusAnnBmDt_Rec20BonusShare']);
                addRowToTable(tableBody, 'Whether Bonus recommended by the Board', newJsonData['bonusRcmndedByBoard_Rec20BonusShare']);
                addRowToTable(tableBody, 'Whether the board discussed on the agenda item prior to deferring the decision on bonus', newJsonData['boardDissAgenda_Rec20BonusShare']);
                addRowToTable(tableBody, 'Whether any Record / Book Closure date intimated earlier', newJsonData['bookClosDtInTieEarlier_Rec20BonusShare']);
                addRowToTable(tableBody, 'Date of intimation of Record / Book closure date', newJsonData['recorBookClosureInTidt_Rec20BonusShare']);
                addRowToTable(tableBody, 'Whether Record / Book closure date fixed by the company', newJsonData['whthrRecorBookClosDtFxd_Rec20BonusShare']);
                addRowToTable(tableBody, 'Whether Date of AGM / EGM / Postal Ballot is Fixed', newJsonData['whthrAgmDtFxdForBonus_Rec20BonusShare']);
                addRowToTable(tableBody, 'Record / Book Closure date', newJsonData['recorBookClosureDt_Rec20BonusShare']);
                addRowToTable(tableBody, 'Record Date', newJsonData['recordDt_Rec20BonusShare']);
                addLabelRowToTable(tableBody, "Book Closure Date");
                addRowToTable(tableBody, 'Start Date Of Book Closure Date', newJsonData['startDtOfBookClosure_Rec20BonusShare']);
                addRowToTable(tableBody, 'End Date Of Book Closure Date', newJsonData['endDtOfBookClosure_Rec20BonusShare']);
                addRowToTable(tableBody, 'Date of AGM / EGM / Postal Ballot', newJsonData['dtOfAgmForBonus_Rec20BonusShare']);
                addRowToTable(tableBody, 'Whether bonus is out of free reserves created out of profits or share premium account', newJsonData['bonusIsOutOfFrReserves_Rec20BonusShare']);
                addRowToTable(tableBody, 'Details of bonus is out of other', newJsonData['dtlsOfBonusIsOut_Rec20BonusShare']);
                addRowToTable(tableBody, 'Bonus ratio', newJsonData['bonusRatio_Rec20BonusShare']);
                addRowToTable(tableBody, 'Free reserves and / or share premium required for implementing the bonus issue', newJsonData['frReservesReqForBonus_Rec20BonusShare']);
                addRowToTable(tableBody, 'Free reserves and / or share premium available for capitalization and the date as on which such balance is available', newJsonData['frReservesReqCapt_Rec20BonusShare']);
                addRowToTable(tableBody, 'Whether the aforesaid figures are audited', newJsonData['whthrFiguresAreAudited_Rec20BonusShare']);
                addRowToTable(tableBody, 'Estimated date by which such bonus shares would be credited/dispatched', newJsonData['estimatedTBonusShareCredit_Rec20BonusShare']);
                addRowToTable(tableBody, 'Paid-up Share capital Before Allotment', newJsonData['paidUpCapShareBefoRallot_Rec20BonusShare']);
                addRowToTable(tableBody, 'Number of paid-up share Before Allotment', newJsonData['noOfPaidShareBefoRallot_Rec20BonusShare']);
                addRowToTable(tableBody, 'Par value', newJsonData['parValueBefoRallotment_Rec20BonusShare']);
                addRowToTable(tableBody, 'Paid-up Share capital After Allotment', newJsonData['paidUpShareCapAfterAllot_Rec20BonusShare']);
                addRowToTable(tableBody, 'Number of paid-up share After Allotment', newJsonData['noOfPaidUpShareAfterAllo_Rec20BonusShare']);
                addRowToTable(tableBody, 'Par value', newJsonData['parValueAfterAllotment_Rec20BonusShare']);
                addRowToTable(tableBody, 'Shorter Notice For Bonus', newJsonData['shorterNoticeForBonus_Rec20BonusShare']);
                addRowToTable(tableBody, 'Remarks', newJsonData['websiteDIssForBonusRmk_Rec20BonusShare']);
            } else if (containerId === 'Rec40Dividend') {
                addRowToTable(tableBody, 'Whether prior intimation of board meeting considering interim / final dividend given to stock exchange', newJsonData['whthrBmCnsdrPropForVd_Rec40Dividend']);
                addRowToTable(tableBody, 'Details if prior intimation of board meeting considering interim / final dividend is not given to stock exchange', newJsonData['ntsBmCnsdrNotGivenForVd_Rec40Dividend']);
                addRowToTable(tableBody, 'Date of Prior Intimation submitted to Stock Exchange on Board Meeting to consider declaration of interim / recommendation of final dividend', newJsonData['priorIntimationSubmittedDt_Rec40Dividend']);
                addRowToTable(tableBody, 'Date of Board Meeting considering declaration of Interim / Recommendation of Final Dividend', newJsonData['recommendationBmDt_Rec40Dividend']);
                addRowToTable(tableBody, 'Meeting Commencement Time', newJsonData['annBmStartTime_Rec40Dividend']);
                addRowToTable(tableBody, 'Meeting Conclusion Time', newJsonData['annBmEndTime_Rec40Dividend']);
                addRowToTable(tableBody, 'Whether Declaration of Interim Dividend / Recommendation of Final Dividend approved by the Board', newJsonData['whthrBoardApproveRecommendation_Rec40Dividend']);
                addRowToTable(tableBody, 'Details If Declaration of Interim Dividend / Recommendation of Final Dividend is not approved/ deferred approved by the Board', newJsonData['ntsBoardNotApproveRecommendation_Rec40Dividend']);
                addRowToTable(tableBody, 'Type of Dividend declared / recommended by the company', newJsonData['firstDividendType_Rec40Dividend']);
                addRowToTable(tableBody, 'Type of Dividend declared / recommended by the company', newJsonData['secondDividendType_Rec40Dividend']);
                addRowToTable(tableBody, 'Type of Dividend declared / recommended by the company', newJsonData['thirdDividendType_Rec40Dividend']);
                addRowToTable(tableBody, 'Details of other type of dividend declared / recommended by the company', newJsonData['recommendedDividendTypeDetails_Rec40Dividend']);
                addLabelRowToTable(tableBody, "Interim Dividend");
                addRowToTable(tableBody, 'Rate of Dividend per equity share', newJsonData['interimDividendRate_Rec40Dividend']);
                addRowToTable(tableBody, 'Date of declaration of Interim Dividend', newJsonData['interimDividendDecisionDt_Rec40Dividend']);
                addRowToTable(tableBody, 'Record Date', newJsonData['interimDividendRecordDt_Rec40Dividend']);
                addRowToTable(tableBody, 'Proposed Date within which payment of dividend shall be made by the company', newJsonData['dividendPaymentProposedDt_Rec40Dividend']);
                addRowToTable(tableBody, 'Period for which dividend is declared', newJsonData['interimDividendPeriod_Rec40Dividend']);
                addLabelRowToTable(tableBody, "Final Dividend");
                addRowToTable(tableBody, 'Rate of Dividend recommended per equity share', newJsonData['finalDividendRate_Rec40Dividend']);
                addRowToTable(tableBody, 'Has Record Date/Book Closure been fixed', newJsonData['whetherRecordFixedForDividend_Rec40Dividend']);
                addRowToTable(tableBody, 'Details if "Record Date/Book Closure has not been fixed"', newJsonData['ntsRecordNotFixedForDividend_Rec40Dividend']);
                addRowToTable(tableBody, 'Record Date/Book Closure Date', newJsonData['fixedRecordBookClosureDt_Rec40Dividend']);
                addRowToTable(tableBody, 'Record Date', newJsonData['finalDividendRecordDt_Rec40Dividend']);
                addLabelRowToTable(tableBody, "Book Closure Date");
                addRowToTable(tableBody, 'Start Date Of Book Closure Date', newJsonData['fixedStartBookClosureDt_Rec40Dividend']);
                addRowToTable(tableBody, 'End Date Of Book Closure Date', newJsonData['fixedEndBookClosureDt_Rec40Dividend']);
                addRowToTable(tableBody, 'Whether Date of General Meeting is fixed for the purpose of Dividend', newJsonData['whetherMeetingDtFixedForDividend_Rec40Dividend']);
                addRowToTable(tableBody, 'Details if "Date of General Meeting is not fixed for the purpose of dividend"', newJsonData['ntsMeetingDtNotFixedForDividend_Rec40Dividend']);
                addRowToTable(tableBody, 'Date of General Meeting', newJsonData['generalMeetingDtForDividend_Rec40Dividend']);
                addRowToTable(tableBody, 'Proposed Date within which payment of dividend shall be made by the company if General Meeting date has been fixed', newJsonData['dividendPaymentProposedDtForFinalDividend_Rec40Dividend']);
                addRowToTable(tableBody, 'Period for which dividend is declared', newJsonData['finalDividendDeclaredPeriod_Rec40Dividend']);
                addLabelRowToTable(tableBody, "Others");
                addRowToTable(tableBody, 'Rate of Dividend recommended per equity share', newJsonData['otherTypeDividendRate_Rec40Dividend']);
                addRowToTable(tableBody, 'Has Record Date/Book Closure been fixed', newJsonData['whetherRecordFixedForOtherTypeDividend_Rec40Dividend']);
                addRowToTable(tableBody, 'Details if "Record Date/Book Closure has not been fixed"', newJsonData['ntsRecordNotFixedForOtherTypeDividend_Rec40Dividend']);
                addRowToTable(tableBody, 'Record Date/Book Closure Date', newJsonData['otherTypeDividendRecordBookClosureDt_Rec40Dividend']);
                addRowToTable(tableBody, 'Record Date', newJsonData['otherTypeDividendRecordDt_Rec40Dividend']);
                addLabelRowToTable(tableBody, "Book Closure Date");
                addRowToTable(tableBody, 'Start Date Of Book Closure Date', newJsonData['otherTypeDividendStartBookClosureDt_Rec40Dividend']);
                addRowToTable(tableBody, 'End Date Of Book Closure Date', newJsonData['otherTypeDividendEndBookClosureDt_Rec40Dividend']);
                addRowToTable(tableBody, 'Whether Date of General Meeting is fixed for the purpose of Dividend', newJsonData['whetherMeetingDtFixedForOtherTypeDividend_Rec40Dividend']);
                addRowToTable(tableBody, 'Details if "Date of General Meeting is not fixed for the purpose of dividend"', newJsonData['ntsMeetingDtNotFixedForOtherTypeDividend_Rec40Dividend']);
                addRowToTable(tableBody, 'Date of General Meeting', newJsonData['generalMeetingDtForOtherTypeDividend_Rec40Dividend']);
                addRowToTable(tableBody, 'Proposed Date within which payment of dividend shall be made by the company if General Meeting date has been fixed', newJsonData['dividendPaymentProposedDtForOtherTypeDividend_Rec40Dividend']);
                addRowToTable(tableBody, 'Period for which dividend is declared', newJsonData['otherTypeDividendDeclaredPeriod_Rec40Dividend']);
                addRowToTable(tableBody, 'Remarks', newJsonData['websiteIssueDividendRemarks_Rec40Dividend']);
            } else if (containerId === 'Rec30BuyBAck') {
                addRowToTable(tableBody, 'Type of Securities', newJsonData['typeOfSecuritiesBB_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Details of Other Securities', newJsonData['otherTypeSecDetailsBB_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Date of Board Meeting to consider the decision on buyback of securities', newJsonData['bmDtToConsdrDecision_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Meeting Commencement Time', newJsonData['startTimeOfBMForBBAnn_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Meeting Conclusion Time', newJsonData['endTimeOfBMForBBAnn_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Whether prior intimation of Board Meeting for considering Buyback of securities filed with the Exchange', newJsonData['whetherBMCnsdrBBWithExch_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Date of Prior intimation of board meeting', newJsonData['dateOfPriorInt_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Details provide if prior intimation of Board Meeting for considering Buyback of securities not filed with the Exchange', newJsonData['ntsBmNotCnsdrBBWithExch_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Whether decision on Buyback of securities approved by the Board', newJsonData['decisionOnBBApproved_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Provide Details if decision on Buyback of securities not approved or Deferred by the Board', newJsonData['ntsDecisionOnBBNotApproved_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Whether the Board discussed on the agenda item prior to deferring the decision on buyback of securities', newJsonData['whetherAgendaDiscussed_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Whether buy-back is less than or equal to 10% of the total paid up equity capital and free reserves of the company', newJsonData['bbLesOrEqUltTenPercentPaidUp_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Whether Date of AGM / EGM / Postal Ballot is fixed by the company', newJsonData['recorBkClosDtInTIEarlier_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Date of AGM / EGM / Postal Ballot', newJsonData['dtOfAgmForBB_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Whether any Record/Book Closure date intimated earlier', newJsonData['recorBookClosDtInTIEarlier_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Date of intimation of Record /Book closure date', newJsonData['recorBookClosureIntIdt_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Whether the mode, quantum, pricing, timing, and other details of buyback decided by the board', newJsonData['whetherModeOrOtherDtlsDecided_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Whether Record /Book closure date is fixed by the company', newJsonData['whetherRecorBookClosureDtFixed_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Record Date/Book Closure Date', newJsonData['recorBookClosureDt_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Record Date', newJsonData['recordDt_Rec30BuyBAck']);
                addLabelRowToTable(tableBody, "Book Closure Date");
                addRowToTable(tableBody, 'Start Date Of Book Closure Date', newJsonData['startDtOfBookClos_Rec30BuyBAck']);
                addRowToTable(tableBody, 'End Date Of Book Closure Date', newJsonData['endDtOfBookClos_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Methods of Buyback', newJsonData['methodOfBB_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Details Of Other Methods of Buyback', newJsonData['otherMethodDtls_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Maximum Buyback size approved by Board of Directors (in INR)', newJsonData['maxBBSizeApproved_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Number of securities proposed for buyback', newJsonData['noOfSecuritiesProposed_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Number of securities proposed for buyback as a percentage of existing paid up capital', newJsonData['noSecPropPrcntOfPaidUp_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Buyback price', newJsonData['bbPrice_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Actual securities in number of existing paid up capital bought back', newJsonData['noOfActualSecurities_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Actual securities in percentage of existing paid up capital bought back', newJsonData['prcntageOfActualSecurities_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Confirmation that the buyback undertaken is not within a period of one year from the date of expiry of the buyback period of the preceding offer of buy-back', newJsonData['cnfrmBBPrdNotWithinExpPrcnt_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Provide Details if not applicable or not confirmed', newJsonData['ntsBBPeriodWithinExpPrcnt_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Confirmation that no shares/other specified securities are issued during the buyback period', newJsonData['cnfrmNoShrIssuedDuringBBPrcnt_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Provide Details if not applicable or not confirmed', newJsonData['ntsShrNotIssuedDuringBBPrcnt_Rec30BuyBAck']);
                addRowToTable(tableBody, 'Remarks', newJsonData['websiteDISSForBBRemarks_Rec30BuyBAck']);
            } else if (containerId === 'Rec50VoluntaryDelist') {
                addRowToTable(tableBody, 'Date of Board Meeting', newJsonData['bmDtForVd_Rec50VoluntaryDelist']);
                addRowToTable(tableBody, 'Meeting Commencement Time', newJsonData['stTimeOfBmForVd_Rec50VoluntaryDelist']);
                addRowToTable(tableBody, 'Meeting Conclusion Time', newJsonData['endTimeOfBmForVd_Rec50VoluntaryDelist']);
                addRowToTable(tableBody, 'Whether prior intimation of board meeting for considering the proposal for voluntary delisting filed with Exchange', newJsonData['whthrBmCnsdrPropForVd_Rec50VoluntaryDelist']);
                addRowToTable(tableBody, 'Whether proposal for voluntary delisting approved / recommended by the Board', newJsonData['whthrPropAprvdForVd_Rec50VoluntaryDelist']);
                addRowToTable(tableBody, 'Whether the board discussed on the agenda item prior to deferring the decision on Voluntary delisting', newJsonData['whthrBmDiscussAgenda_Rec50VoluntaryDelist']);
                addRowToTable(tableBody, 'Type of Voluntary Delisting', newJsonData['typeOfVd_Rec50VoluntaryDelist']);
                addLabelRowToTable(tableBody, "Details from some of the recognised stock exhanges");
                addRowToTable(tableBody, 'Name of the Stock Exchange from which the company decided to delist its securities', newJsonData['exchNameFromWhichDelist_Rec50VoluntaryDelist']);
                addRowToTable(tableBody, 'Exchange on which company continues to remain listed', newJsonData['exchOnWhichRemainListed_Rec50VoluntaryDelist']);
                addRowToTable(tableBody, 'Reason for Delisting', newJsonData['reasonForListingFromSmExch_Rec50VoluntaryDelist']);
                addLabelRowToTable(tableBody, "Delisting from all the recognised stock exhanges");
                addRowToTable(tableBody, 'Whether the company to be delisted is a small company and satisfies the conditions specified under Regulation 35 (1) of SEBI (Delisting of Equity Shares) Regulations, 2021', newJsonData['dlstedCompSatisfiesConditions_Rec50VoluntaryDelist']);
                addRowToTable(tableBody, 'Date of Initial Public Announcement made to Stock Exchange', newJsonData['initialPublicAnnDt_Rec50VoluntaryDelist']);
                addLabelRowToTable(tableBody, "Whether the board certified the following");
                addRowToTable(tableBody, 'The company is in compliance with the applicable provisions of securities laws', newJsonData['compInComplianceWithLaws_Rec50VoluntaryDelist']);
                addRowToTable(tableBody, 'Details if the company is not in compliance with the applicable provisions of securities laws', newJsonData['ntsCompNotInComplianceWithLaw_Rec50VoluntaryDelist']);
                addRowToTable(tableBody, 'the acquirer and its related entities are in compliance with the applicable provisions of securities laws in terms of the report of the Company Secretary including compliance with sub-regulation (5) of regulation 4 of SEBI Delisting Regulations', newJsonData['relaEntInComplianceWithLaws_Rec50VoluntaryDelist']);
                addRowToTable(tableBody, 'Details if the acquirer and its related entities are not in compliance with the applicable provisions of securities laws in terms of the report of the Company Secretary including compliance with sub-regulation (5) of regulation 4 of SEBI Delisting Regulations', newJsonData['ntrltdEntNotInComplianceWithLaw_Rec50VoluntaryDelist']);
                addRowToTable(tableBody, 'The delisting, in their opinion, is in the interest of the shareholders of the company', newJsonData['inInterestOfShareholdersOfComp_Rec50VoluntaryDelist']);
                addRowToTable(tableBody, 'Details if the delisting, in their opinion, is not in the interest of the shareholders of the company', newJsonData['ntsNotInInterestOfShareholdersComp_Rec50VoluntaryDelist']);
                addRowToTable(tableBody, 'Reason for Delisting', newJsonData['reasonForListingFromAllExch_Rec50VoluntaryDelist']);
                addRowToTable(tableBody, 'Whether date of AGM / EGM / Postal Ballot is Fixed', newJsonData['agmDtIsFixedDelistingAllExch_Rec50VoluntaryDelist']);
                addRowToTable(tableBody, 'Date of AGM or EGM or postal ballot for delisting of the company', newJsonData['dtOfAgmForDelisting_Rec50VoluntaryDelist']);
                addRowToTable(tableBody, 'Name of Merchant Banker registered with the SEBI', newJsonData['mrchntBankerNameRegdSebi_Rec50VoluntaryDelist']);
                addRowToTable(tableBody, 'Due diligence has been carried out by a peer review company secretary', newJsonData['peerReviewCompSecretary_Rec50VoluntaryDelist']);
                addLabelRowToTable(tableBody, "Delisting of subsidiary company pursuant to a scheme of arrangement");
                addRowToTable(tableBody, 'Whether date of AGM / EGM / Postal Ballot is Fixed', newJsonData['agmDtIsFixedForDelistingSbsidry_Rec50VoluntaryDelist']);
                addRowToTable(tableBody, 'Date of AGM or EGM or postal ballot for delisting of subsidiary company', newJsonData['dateOfAgmOrEgm_Rec50VoluntaryDelist']);
                addRowToTable(tableBody, 'Delay in conducting the Board Meeting', newJsonData['notesVdFilledWithExch_Rec50VoluntaryDelist']);
                addRowToTable(tableBody, 'Remarks', newJsonData['websiteDissForVdRemarks_Rec50VoluntaryDelist']);
            } else if (containerId === 'Rec20ISDPreOpenBuyback') {
                addRowToTable(tableBody, 'Date of Public Announcement', newJsonData['dateOfPublicAnn_Rec20ISDPreOpenBuyback']);
                addRowToTable(tableBody, 'Buyback Opening Date', newJsonData['dateOfBBOpening_Rec20ISDPreOpenBuyback']);
                addRowToTable(tableBody, 'Buyback Closing Date', newJsonData['dateOfBBClosing_Rec20ISDPreOpenBuyback']);
                addRowToTable(tableBody, 'Maximum Buyback Price (Rs.)', newJsonData['maxBBPrice_Rec20ISDPreOpenBuyback']);
                addRowToTable(tableBody, 'Maximum No of shares to be bought back', newJsonData['maxSharesToBuyBack_Rec20ISDPreOpenBuyback']);
                addRowToTable(tableBody, 'Company’s Broker/ Buyer Broker (Name)', newJsonData['nameOfBuyerBkr_Rec20ISDPreOpenBuyback']);
                addRowWithTwoColumnsAndHeader(tableBody, "Manager to Buyback Offer", newJsonData['nameOfMngrToBBOffr_Rec20ISDPreOpenBuyback'], newJsonData['emailMngrToBBOffr_Rec20ISDPreOpenBuyback'], 'Name', 'Email ID');
                addRowToTable(tableBody, 'Board Meeting Date', newJsonData['dateOfBoardMeeting_Rec20ISDPreOpenBuyback']);
                addRowToTable(tableBody, 'Shareholders Resolution Date, if applicable', newJsonData['dateOfResolutionSH_Rec20ISDPreOpenBuyback']);
                addRowToTable(tableBody, 'Listed Capital (No. of Shares)', newJsonData['sharesListedCap_Rec20ISDPreOpenBuyback']);
                addRowWithTwoColumnsAndHeader(tableBody, "Promoter(s) holding Pre Buyback", newJsonData['sharesPHPreBBPreIsue_Rec20ISDPreOpenBuyback'], newJsonData['prcentOfSharesPHPreBBPre_Rec20ISDPreOpenBuyback'], "No. of Shares", "Percentage");
                addRowToTable(tableBody, 'Any other disclosure w.r.t. compliance of any SEBI Act, Regulation, Circular or provision', newJsonData['anyOtherDisclosure_Rec20ISDPreOpenBuyback']);
                addRowToTable(tableBody, 'Remarks', newJsonData['rmksWebDiss_Rec20ISDPreOpenBuyback']);
                addRowToTable(tableBody, 'Notes', newJsonData['notesForBBOpenOfr_Rec20ISDPreOpenBuyback']);
            } else if (containerId === 'Rec30ISDPostOpenBuyback') {
                addRowToTable(tableBody, 'Total No of shares bought back', newJsonData['totalNumShrToBuyBack_Rec30ISDPostOpenBuyback']);
                addRowToTable(tableBody, 'Date of Closure of Buyback', newJsonData['dateOfBBClosure_Rec30ISDPostOpenBuyback']);
                addRowToTable(tableBody, 'Post Buyback Capital (No. of shares)', newJsonData['numShrCapitalPostBB_Rec30ISDPostOpenBuyback']);
                addRowToTable(tableBody, 'Date of Post Buy Back Public Announcement', newJsonData['dateOfPostBBAnn_Rec30ISDPostOpenBuyback']);
                addRowWithTwoColumnsAndHeader(tableBody, "Promoter(s) holding Post Buyback", newJsonData['numShrPHPreBBPost_Rec30ISDPostOpenBuyback'], newJsonData['percentSharesPHPreBBPost_Rec30ISDPostOpenBuyback'], 'No. of Shares', 'Percentage');
                addRowToTable(tableBody, 'Any other disclosure w.r.t. compliance of any SEBI Act, Regulation, Circular or provision', newJsonData['anyOtherDisclosure_Rec30ISDPostOpenBuyback']);
                addRowToTable(tableBody, 'Remarks', newJsonData['rmksWebDiss_Rec30ISDPostOpenBuyback']);
                addRowToTable(tableBody, 'Notes', newJsonData['notesForBBOpen_Rec30ISDPostOpenBuyback']);
            } else if (containerId === 'Rec30ISDPostTenderBuyback') {
                addRowToTable(tableBody, 'Date of post buyback public announcement', newJsonData['dtOfPostBBPblcAnn_Rec30ISDPostTenderBuyback']);
                addLabelRowToTable(tableBody, "Details of Issued, subscribed and paid-up number of shares post-buyback");
                addRowToTable(tableBody, 'Number of Shares issued post buyback', newJsonData['numShrIssPostBB_Rec30ISDPostTenderBuyback']);
                addRowToTable(tableBody, 'Number of Shares subscribed post buyback', newJsonData['numShrSubscrPostBB_Rec30ISDPostTenderBuyback']);
                addRowToTable(tableBody, 'Number of Shares paid up post buyback', newJsonData['numShrPdPostBB_Rec30ISDPostTenderBuyback']);
                addLabelRowToTable(tableBody, "Details of Issued, subscribed and paid-up number of shares pre-buyback");
                addRowToTable(tableBody, 'Number of Shares issued pre buyback', newJsonData['numShrIssPreBB_Rec30ISDPostTenderBuyback']);
                addRowToTable(tableBody, 'Number of Shares subscribed pre buyback', newJsonData['numShrSubPreBB_Rec30ISDPostTenderBuyback']);
                addRowToTable(tableBody, 'Number of Shares paid up pre buyback', newJsonData['numShrPdPreBB_Rec30ISDPostTenderBuyback']);
                addRowToTable(tableBody, 'Total number of Equity Shares bought back pursuant to the Buyback', newJsonData['ttlNumEqtyShrBkBB_Rec30ISDPostTenderBuyback']);
                addRowToTable(tableBody, 'Total amount utilized in the Buyback', newJsonData['ttlAmntUtlInBB_Rec30ISDPostTenderBuyback']);
                addRowWithTwoColumns(tableBody, "", "No. of Shares", "Percentage");
                addRowWithTwoColumns(tableBody, "Promoter(s) holding Pre Buyback", newJsonData['numShrPrmtrHldgPreBB_Rec30ISDPostTenderBuyback'], newJsonData['prcntgPrmtrPreBBPost_Rec30ISDPostTenderBuyback']);
                addRowWithTwoColumns(tableBody, "Promoter(s) tentative holding Post Buyback", newJsonData['numShrPrmtrTenHldgPostBB_Rec30ISDPostTenderBuyback'], newJsonData['prcntgShrPrmtrPostBB_Rec30ISDPostTenderBuyback']);
                addRowToTable(tableBody, 'Any other disclosure w.r.t. compliance of any SEBI Act, Regulation, Circular or provision', newJsonData['anyOthrDiscPstBB_Rec30ISDPostTenderBuyback']);
                addRowToTable(tableBody, 'Remarks', newJsonData['rmrksWebRmkrPostBB_Rec30ISDPostTenderBuyback']);
                addRowToTable(tableBody, 'Notes', newJsonData['ntsBBTndrRtPostBB_Rec30ISDPostTenderBuyback']);
            } else if (containerId === 'Rec20ISDPreTenderBuyback') {
                addRowToTable(tableBody, 'Board Meeting Date', newJsonData['dtOfBrdMtng_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Date of declaration of results of the postal ballot, if applicable', newJsonData['dtOfDclrRsltPstlBlt_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Date of Public Announcement', newJsonData['dtOfPblcAnn_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Record date', newJsonData['dtOfRcrdBB_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Buyback opening date', newJsonData['dtOfBBOpen_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Buyback closing date', newJsonData['dtOfBBClose_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Buyback offer (No. of Share)', newJsonData['numOfShrBBOfr_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Buyback price (Per share)', newJsonData['bbPricePrShare_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Aggregate consideration not exceeding (Amount in Rs.)', newJsonData['amntAggrCnsdr_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Equity shares reserved for small shareholders (No. of Share)', newJsonData['numOfEqutShrSmlShrhldr_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Equity shares reserved for general category (No. of Share)', newJsonData['numOfEqutShrGenCatg_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Participation by promoter(s)', newJsonData['whthrPrtcpntPrmtr_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Promoter(s) declared Its intention to tender shares up to (No. of Share)', newJsonData['numOfShrPrmtrDeclInOrdr_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Details of the escrow account (Bank Name)', newJsonData['nmOfBnkExcAcc_Rec20ISDPreTenderBuyback']);
                addRowWithTwoColumns(tableBody, "", "No. of Shares", "Percentage");
                addRowWithTwoColumns(tableBody, "Promoter(s) holding Pre Buyback", newJsonData['numOfShrPrmtrHldng_Rec20ISDPreTenderBuyback'], newJsonData['prcntgShrPrmtrHldng_Rec20ISDPreTenderBuyback']);
                addRowWithTwoColumns(tableBody, "Promoter(s) tentative holding Post Buyback", newJsonData['numShrPrmtrTentHldng_Rec20ISDPreTenderBuyback'], newJsonData['prcntgShrPrmtrTentHldng_Rec20ISDPreTenderBuyback']);
                addLabelRowToTable(tableBody, "Name of the exchange(s) where company is listed");
                var stockData = newJsonData['nmStkExchComList_Rec20ISDPreTenderBuyback'].split(",") || '';
                addRowToTable(tableBody, 'Stock Exchange 1', stockData[0] || '-');
                addRowToTable(tableBody, 'Stock Exchange 2', stockData[1] || '-');
                addRowToTable(tableBody, 'Stock Exchange 3', stockData[2] || '-');
                addRowToTable(tableBody, 'Stock Exchange 4', stockData[3] || '-');
                addRowToTable(tableBody, 'Designated stock exchange', newJsonData['designStkExch_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Company’s Broker/ Buyer Broker (Name)', newJsonData['nmOfBrkrCompBuyrBrkr_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Company’s Broker/ Buyer Broker (Code of the Broker)', newJsonData['codOfBrkrCompBuyrBrkr_Rec20ISDPreTenderBuyback']);
                addLabelRowToTable(tableBody, "Details of Manager(s) to the Buyback (Investment Banker)");
                addRowToTable(tableBody, 'Name', newJsonData['nmOfInvstBanker_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Telephone', newJsonData['telphnOfInvstBanker_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Email ID', newJsonData['emlInvstBanker_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Website', newJsonData['webSiteInvstBanker_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Last date for the receipt of completed tender forms and other specified documents including physical share certificates (as applicable) by the Registrar', newJsonData['lstDtRcptComplTndr_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Last date for providing acceptance or non-acceptance to the Stock Exchange by the Registrar to the buyback', newJsonData['lstDtPrvdAccOrNonAcc_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Last date for settlement of bids on the Stock Exchanges', newJsonData['lstDtStlmntBds_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Last date for return of unaccepted equity shares by Stock Exchanges to Eligible Shareholders or Stock Brokers', newJsonData['lstDtRtrnUnaccShr_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Last date for payment of consideration to Eligible Shareholders who participated in the Buyback', newJsonData['lstDtPaymntElgbl_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Last date for extinguishment of buyback equity shares', newJsonData['lstDtExtingBBShr_Rec20ISDPreTenderBuyback']);
                addLabelRowToTable(tableBody, "Details Registrar to Offer");
                addRowToTable(tableBody, 'Name', newJsonData['nmOfRegstrToOfr_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Telephone', newJsonData['telphnRegstrOfr_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Email ID', newJsonData['emlRegstrToOfr_Rec20ISDPreTenderBuyback']);
                addLabelRowToTable(tableBody, "Details of Company Secretary");
                addRowToTable(tableBody, 'Name', newJsonData['nmOfCompSec_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Membership Number', newJsonData['mmbrshpNumCompSec_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Mobile', newJsonData['mblOfCompSec_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Email ID', newJsonData['emailCompSec_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Any other disclosure w.r.t. compliance of any SEBI Act, Regulation, Circular or provision', newJsonData['anyOthrDiscCompl_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Remarks', newJsonData['remrkWebDismBBTndr_Rec20ISDPreTenderBuyback']);
                addRowToTable(tableBody, 'Notes', newJsonData['ntsBBTndrRoutPreStg_Rec20ISDPreTenderBuyback']);
            } else if (containerId === 'RecISDTakeoverPre') {

                var stockBrokerJson = [{
                    "name": "sr_no",
                    "heading": "Sr. No",
                    "subHead": "",
                    "width": "10%"
                }, {
                    "name": "nameOfStockBroker_stockBrokerDetailsResponse",
                    "heading": "Name of Stock Broker appointed by acquirer",
                    "subHead": "",
                    "width": "45%"
                }, {
                    "name": "stockBrokerContactDetails_stockBrokerDetailsResponse",
                    "heading": "Contact details of Stock Broker appointed by acquirer",
                    "subHead": "",
                    "width": "45%"
                }];
                customTableCreate(containerId, 'table-stockBrokerDetailsResponse', stockBrokerJson, data[0].stockBrokerDetailsResponse || [], 'Details of Stock Broker appointed by acquirer');

                var companySecretaryJson = [{
                    "name": "sr_no",
                    "heading": "Sr. No",
                    "subHead": "",
                    "width": "10%"
                }, {
                    "name": "nameOfCompanySecretary_companySecretaryDetailsResponse",
                    "heading": "Name of Company Secretary",
                    "subHead": "",
                    "width": "45%"
                }, {
                    "name": "companySecretaryCotactDetails_companySecretaryDetailsResponse",
                    "heading": "Contact details of Company Secretary",
                    "subHead": "",
                    "width": "45%"
                }];
                customTableCreate(containerId, 'table-companySecretary', companySecretaryJson, data[0].companySecretaryDetailsResponse || [], 'Details of Name of Company Secretary');

                var managerJson = [{
                    "name": "sr_no",
                    "heading": "Sr. No",
                    "subHead": "",
                    "width": "10%"
                }, {
                    "name": "nameOFManager_managerDetailsResponse",
                    "heading": "Name of manager(s) to the offer",
                    "subHead": "",
                    "width": "30%"
                }, {
                    "name": "nameOfOtherLM_managerDetailsResponse",
                    "heading": "Name of other LM/BRLM",
                    "subHead": "",
                    "width": "30%"
                }, {
                    "name": "managerContactDetails_managerDetailsResponse",
                    "heading": "Contact details of manager(s) to the offer",
                    "subHead": "",
                    "width": "30%"
                }];
                customTableCreate(containerId, 'table-manager', managerJson, data[0].managerDetailsResponse || [], 'Details of Manager(s) to the offer');

                var AcquirerJson = [{
                    "name": "sr_no",
                    "heading": "Sr. No",
                    "subHead": "",
                    "width": "10%"
                }, {
                    "name": "nameOfAcquirer_AcquirerDetailsResponse",
                    "heading": "Name of Acquirer(s)",
                    "subHead": "",
                    "width": "30%"
                }];
                customTableCreate(containerId, 'table-AcquirerDetailsResponse', AcquirerJson, data[0].AcquirerDetailsResponse || [], 'Details of Acquirer(s)');

                var PersonActingJson = [{
                    "name": "sr_no",
                    "heading": "Sr. No",
                    "subHead": "",
                    "width": "20%"
                }, {
                    "name": "personActingInConcert_PersonActingInConcertResponse",
                    "heading": "Name of Person(s) Acting in Concert",
                    "subHead": "",
                    "width": "80%"
                }];
                customTableCreate(containerId, 'table-PersonActingInConcertResponse', PersonActingJson, data[0].PersonActingInConcertResponse || [], 'Details of Person(s) Acting in Concert');
            } else if (containerId === 'masterRemarkOpenOfferPost') {
                addRowToTable(tableBody, 'Offer price per fully Paid up share', newJsonData['offerPriceFullyPaid_masterRemark']);
                addRowToTable(tableBody, 'Offer price per Partly Paid up share', newJsonData['offerPricePartlyPaid_masterRemark']);
                addRowToTable(tableBody, 'Date of payment/settlement*', newJsonData['dateOfPaySet_masterRemark']);
                addRowToTable(tableBody, 'Consideration paid in open offer ( Rs. In Million)*', newJsonData['amtConsPaid_masterRemark']);
                addRowToTable(tableBody, 'Detail of interest paid due to delay in payment (Amount)*', newJsonData['detIntDueToDelay_masterRemark']);
                addRowToTable(tableBody, 'Notes', newJsonData['notes_masterRemark']);
            } else if (containerId === 'isdPreVoluntaryMaster') {
                var isdPreVoluntaryMain = newJsonData.masterRemark[0] || {};
                addRowToTable(tableBody, 'Registered Office Address of the Company', isdPreVoluntaryMain['regOfficeAddOfComp_masterRemark']);
                addRowToTable(tableBody, 'Corporate Office Address of the Company', isdPreVoluntaryMain['corpOfficeAddOfComp_masterRemark']);
                addLabelRowToTable(tableBody, "Shareholding of promotor & promoter group");
                addRowToTable(tableBody, 'Number Of Shareholding Promoter And Promoter Group', isdPreVoluntaryMain['numOfSHPromAndPromGrp_masterRemark']);
                addRowToTable(tableBody, 'Percentage Of Shareholding Promoter And Promoter Group', isdPreVoluntaryMain['prcntOfSHPromAndPromGrp_masterRemark'] + '%');
                addRowToTable(tableBody, 'Website', isdPreVoluntaryMain['websiteOfTheCompany_masterRemark']);
                addRowToTable(tableBody, 'Exchanges Where Listed', isdPreVoluntaryMain['exchgWhereListed_masterRemark']);
                addRowToTable(tableBody, 'Platform', isdPreVoluntaryMain['platformForVolDel_masterRemark']);
                addRowToTable(tableBody, 'Delisting Type', isdPreVoluntaryMain['delistingType_masterRemark']);
                addRowToTable(tableBody, 'Name Of Registrar To Offer', isdPreVoluntaryMain['nameOfRegToOffer_masterRemark']);
                addRowToTable(tableBody, 'Details Of Other Registrar To Offer', isdPreVoluntaryMain['dtlsOfOtherRegToOffer_masterRemark']);
                addRowToTable(tableBody, 'Email ID Of Registrar To Offer', isdPreVoluntaryMain['emailIdOfRegToOffer_masterRemark']);
                addRowToTable(tableBody, 'Helpline Number Of Registrar To Offer', isdPreVoluntaryMain['helplineNumOfRegToOffer_masterRemark']);
                addRowToTable(tableBody, 'Managers To The Offer', isdPreVoluntaryMain['mngrsToTheOffer_masterRemark']);
                addRowToTable(tableBody, 'Email ID Of Manager To Offer', isdPreVoluntaryMain['emailOfMngrToOffer_masterRemark']);
                addRowToTable(tableBody, 'Helpline Number Of Manager To Offer', isdPreVoluntaryMain['helplineNumOfMgrToOffer_masterRemark']);
                addRowToTable(tableBody, 'Delisting From', isdPreVoluntaryMain['delistingFrom_masterRemark']);
                addRowToTable(tableBody, 'Reason Of Delisting', isdPreVoluntaryMain['reasonOfDelisting_masterRemark']);
                addRowToTable(tableBody, 'Date of approval of Board of Directors in respect of the proposal of the acquirer to delist the equity shares', isdPreVoluntaryMain['dtOfApprovalBODsToDelistTheEqSh_masterRemark']);
                addRowToTable(tableBody, 'Reference date for determination of floor price', isdPreVoluntaryMain['dtOfRefDetOfFlrPrice_masterRemark']);
                addRowToTable(tableBody, 'Floor Price (Rs. Per Equity Share)', isdPreVoluntaryMain['floorPrice_masterRemark']);
                addRowToTable(tableBody, 'Indicative Price if any (Rs. Per Equity Share)', isdPreVoluntaryMain['indicativePrice_masterRemark']);
                addRowToTable(tableBody, 'Revised Indicative price if any (Rs. Per Equity Share)', isdPreVoluntaryMain['revIndicativePrice_masterRemark']);
                addRowToTable(tableBody, 'Date of revised Indicative price', isdPreVoluntaryMain['dtOfRevIndicativePrice_masterRemark']);
                addRowToTable(tableBody, 'Date of approval of shareholders through special resolution', isdPreVoluntaryMain['dtOfApprOfSHThrghSplResl_masterRemark']);
                addRowToTable(tableBody, 'Date of In-principle approval granted by the Stock Exchanges', isdPreVoluntaryMain['dtOfIPApprGrantedByTheStockExch_masterRemark']);
                addRowToTable(tableBody, 'Specified date for determining the names of the shareholders to whom the letter of offer shall be sent', isdPreVoluntaryMain['dtOfNameSHLetterSent_masterRemark']);
                addRowToTable(tableBody, 'Designated stock exchange', isdPreVoluntaryMain['designatedStockExchange_masterRemark']);
                addRowToTable(tableBody, 'Tendering Start Date', isdPreVoluntaryMain['dtOfStartOfTendering_masterRemark']);
                addRowToTable(tableBody, 'Last date for upward revision or withdrawal of bids', isdPreVoluntaryMain['dtOfLastUpwRevOrWitdrOfBids_masterRemark']);
                addRowToTable(tableBody, 'Tendering closing date', isdPreVoluntaryMain['dtOfEndOfTendering_masterRemark']);
                addRowToTable(tableBody, 'Last date for announcement of counter offer', isdPreVoluntaryMain['dtOfLastAnnOfCountOffr_masterRemark']);
                addRowToTable(tableBody, 'Last date for Public Announcement regarding success or failure of the Delisting Offer', isdPreVoluntaryMain['dtOfLstPubAnnRegrdSuccsFailDelist_masterRemark']);
                addRowToTable(tableBody, 'Proposed date for payment of consideration to public shareholders who validly tendered in the delisting offer', isdPreVoluntaryMain['dtOfPropPaymOfConsToPubSHWhoValTendInTheDelOffr_masterRemark']);
                addRowToTable(tableBody, 'Notes', isdPreVoluntaryMain['notsDelPreExplTxtBlock_masterRemark']);
                // addRowToTable(tableBody, 'Notes For Platform', isdPreVoluntaryMain['notesForPlatform_masterRemark']);
            } else if (containerId === 'isdPostVoluntaryMaster') {
                var isdPostVoluntaryMain = newJsonData.masterRemark[0] || {};
                addRowToTable(tableBody, 'Discovered price (Rs. Per Equity Share)', isdPostVoluntaryMain['discPriceAsPerRegltn20_masterRemark']);
                addRowToTable(tableBody, 'Exit Price per Equity Share, if higher than the discovered price (Pursuant to Regulation 20(6) of SEBI Delisting Regulations)', isdPostVoluntaryMain['priceHighDiscovrdPriceReg6OfReg20_masterRemark']);
                addRowToTable(tableBody, 'Date of counter offer', isdPostVoluntaryMain['dtOfCounterOffer_masterRemark']);
                addRowToTable(tableBody, 'Counter offer price (Rs. Per Equity Share)', isdPostVoluntaryMain['counterOfferPrice_masterRemark']);
                addRowToTable(tableBody, 'Book value per equity share if counter offer is provided (per regulation 22(5) of the SEBI Delisting of Equity Shares Regulations, 2021) (Rs. Per Equity Share)', isdPostVoluntaryMain['bookValueSubReg5OfReg22_masterRemark']);
                addRowToTable(tableBody, 'Date of payment/ settlement', isdPostVoluntaryMain['dtOfPayOrSettlement_masterRemark']);
                addRowToTable(tableBody, 'Consideration paid in voluntary delisting (Rs. In Million)', isdPostVoluntaryMain['amtOfConsidPaidInVolDel_masterRemark']);
                addRowToTable(tableBody, 'Detail of interest paid due to delay in payment (Rs.)', isdPostVoluntaryMain['dtlsOfInterestPaidDueToDelayInPay_masterRemark']);
                addLabelRowToTable(tableBody, "Post Offer Shareholding of Public");
                addRowToTable(tableBody, 'Number of shares', isdPostVoluntaryMain['numOfSharesPostOfferPubSH_masterRemark']);
                addRowToTable(tableBody, 'Percentage of shares', isdPostVoluntaryMain['percOfSharesPostOfferPubSH_masterRemark'] + ' %');
                addRowToTable(tableBody, 'Date of issuance of final notice for voluntary delisting by the Stock Exchange', isdPostVoluntaryMain['dtOfIssuanceOfFinalNoticeForVDStockExch_masterRemark']);
                addRowToTable(tableBody, 'Last date for remaining shareholders to tender equity shares', isdPostVoluntaryMain['dtOfEndRemSHToTenderEqtyShr_masterRemark']);
                addRowToTable(tableBody, 'Effective date of delisting (as mentioned in Exchange\'s final notice)', isdPostVoluntaryMain['dtOfVolDelEffc_masterRemark']);
                addRowToTable(tableBody, 'Notes', isdPostVoluntaryMain['notesForVDPostExplTextBlock_masterRemark']);
            } else {
                for (var key in newJsonData) {
                    if (newJsonData.hasOwnProperty(key)) {
                        var row = document.createElement("tr");

                        var label = key;
                        if (keyMapping.hasOwnProperty(key)) {
                            label = keyMapping[key];
                        }

                        var keyCell = document.createElement("td");
                        keyCell.textContent = label;
                        keyCell.style.width = "50%"; // Set width of first column
                        keyCell.setAttribute("class", "xbrlrows");
                        row.appendChild(keyCell);
                        var valueCell = document.createElement("td");
                        var cellText = newJsonData[key] !== null ? newJsonData[key].toString() : "";
                        valueCell.textContent = cellText;
                        valueCell.setAttribute("class", "xbrlrows");
                        valueCell.style.width = "50%"; // Set width of first column

                        // Check if the content of the cell exceeds 200px in height and add the div accordingly
                        if (label === "Details of Resolution/Agenda") {
                            var linkElement = document.createElement("a");
                            linkElement.textContent = "Click Here";
                            linkElement.setAttribute("href", "#");
                            linkElement.addEventListener("click", function () {
                                activateTabWithLabel("Details of Resolution/Agenda");
                            });
                            valueCell.innerHTML = ''; // Clear the cell content before appending the link
                            valueCell.appendChild(linkElement);
                        } else if (isContentOverflowing(cellText)) {
                            var divElement = document.createElement("div");
                            divElement.textContent = cellText;
                            divElement.style.maxHeight = "200px";
                            divElement.style.overflowY = "auto";
                            valueCell.innerHTML = ''; // Clear the cell content before appending the div
                            valueCell.appendChild(divElement);
                        }

                        row.appendChild(valueCell);

                        tableBody.appendChild(row);
                    }
                }
            }
        }

        _table.appendChild(tableBody);
        tableContainer.appendChild(_table);
    }
    $('table.common_table caption').remove();

    if (containerId === 'isdPreVoluntaryMaster') {

        var Rec20PreVoluntaryJson = [{
            "name": "sr_no",
            "heading": "Sr. No",
            "subHead": "",
            "width": "10%"
        }, {
            "name": "nameOfPromoter_Rec20PreVoluntary",
            "heading": "Name Of Promoters",
            "subHead": "",
            "width": "45%"
        }, {
            "name": "addressOfPromoter_Rec20PreVoluntary",
            "heading": "Address Of Promoters",
            "subHead": "",
            "width": "45%"
        }];
        customTableCreate(containerId, 'table-Rec20PreVoluntary', Rec20PreVoluntaryJson, data[0].Rec20PreVoluntary || [], 'Details of Promoters');

        var rec30prevoluntaryJson = [{
            "name": "sr_no",
            "heading": "Sr. No",
            "subHead": "",
            "width": "10%"
        }, {
            "name": "nameOfCompany_Rec30PreVoluntary",
            "heading": "Name Of Company Secretary And Compliance Officer",
            "subHead": "",
            "width": "45%"
        }, {
            "name": "emailId_Rec30PreVoluntary",
            "heading": "Email ID",
            "subHead": "",
            "width": "45%"
        }];
        customTableCreate(containerId, 'table-rec30prevoluntary', rec30prevoluntaryJson, data[0].Rec30PreVoluntary || [], 'Details of CS and Compliance Officer');

        var rec40prevoluntaryJson = [{
            "name": "sr_no",
            "heading": "Sr. No",
            "subHead": "",
            "width": "10%"
        }, {
            "name": "nameOfAcquirers_Rec40PreVoluntary",
            "heading": "Name of the Acquirers",
            "subHead": "",
            "width": "30%"
        }, {
            "name": "numberOfShares_Rec40PreVoluntary",
            "heading": "Number of shares",
            "subHead": "",
            "width": "30%"
        }, {
            "name": "percOfShareholding_Rec40PreVoluntary",
            "heading": "Percentage of shareholding",
            "subHead": "",
            "width": "30%"
        }];
        customTableCreate(containerId, 'table-rec40prevoluntary', rec40prevoluntaryJson, data[0].Rec40PreVoluntary || [], 'Details of Acquirer');

        var Rec50PreVoluntaryJson = [{
            "name": "sr_no",
            "heading": "Sr. No",
            "subHead": "",
            "width": "10%"
        }, {
            "name": "namePersonActConcert_Rec50PreVoluntary",
            "heading": "Name Of Person Acting In Concert",
            "subHead": "",
            "width": "30%"
        }, {
            "name": "numberOfShares_Rec50PreVoluntary",
            "heading": "Number Of Shares",
            "subHead": "",
            "width": "30%"
        }, {
            "name": "percOfShareholding_Rec50PreVoluntary",
            "heading": "Percentage Of Shareholding",
            "subHead": "",
            "width": "30%"
        }];
        customTableCreate(containerId, 'table-Rec50PreVoluntary', Rec50PreVoluntaryJson, data[0].Rec50PreVoluntary || [], 'Details of Acting in Concert');
    }
    if (containerId === 'isdPostVoluntaryMaster') {

        var Rec20PostVoluntaryJson = [{
            "name": "sr_no",
            "heading": "Sr. No",
            "subHead": "",
            "width": "10%"
        }, {
            "name": "nameOfacqorpac_Rec20PostVoluntary",
            "heading": "Name of Acquirer / PAC",
            "subHead": "",
            "width": "20%"
        }, {
            "name": "acqOrPac_Rec20PostVoluntary",
            "heading": "Acquirer / PAC",
            "subHead": "",
            "width": "20%"
        }, {
            "name": "numOfShares_Rec20PostVoluntary",
            "heading": "Number Of Shares",
            "subHead": "",
            "width": "20%"
        }, {
            "name": "percOfShares_Rec20PostVoluntary",
            "heading": "Percentage Of Shares",
            "subHead": "",
            "width": "20%"
        },,];
        customTableCreate(containerId, 'table-Rec20PostVoluntary', Rec20PostVoluntaryJson, data[0].Rec20PostVoluntary || [], 'Details of Acquirer / PAC');
    }

    // Add additional table for Rec30BuyBAck
    if (containerId === "Rec30BuyBAck") {
        for (var j = 0; j < data.length; j++) {
            var rowData = data[j];
            // Rec30BuyBAck Pre Table Starts
            var Rec30BuyBAckPre = document.createElement("table");
            Rec30BuyBAckPre.classList.add("common_table", "customHeight-table", "table", "table-bordered", "jsonTable");
            var Rec30BuyBAckPreContainer = document.createElement("div");
            var Rec30BuyBAckPreLabel = document.createElement("h4");
            Rec30BuyBAckPreLabel.classList.add("section-heading");
            Rec30BuyBAckPreLabel.textContent = "Pre-Buyback Shareholding Pattern";
            Rec30BuyBAckPreContainer.appendChild(Rec30BuyBAckPreLabel);

            // table header
            var Rec30BuyBAckPreHeader = document.createElement("thead");
            var Rec30BuyBAckPreHeaderRow = document.createElement("tr");
            var Rec30BuyBAckPreHeaders = ["Category of Shareholders", "Number of Shares", "% of Existing Capital"];
            for (var _j = 0; _j < Rec30BuyBAckPreHeaders.length; _j++) {
                var Rec30BuyBAckPreHeaderCell = document.createElement("th");
                Rec30BuyBAckPreHeaderCell.textContent = Rec30BuyBAckPreHeaders[_j];
                Rec30BuyBAckPreHeaderRow.appendChild(Rec30BuyBAckPreHeaderCell);
            }
            Rec30BuyBAckPreHeader.appendChild(Rec30BuyBAckPreHeaderRow);

            var Rec30BuyBAckPreBody = document.createElement("tbody");

            var Rec30BuyBAckPreRows = [["Promoter & Promotor Group", rowData.preBBShareUnderPromoterCat_Rec30BuyBAck, rowData.preBBPromotShrCapitalPrcnt_Rec30BuyBAck], ["Public (B)", rowData.preBBShareUnderPublicCat_Rec30BuyBAck, rowData.preBBPublicShrCapitalPrcnt_Rec30BuyBAck], ["Others (C)", rowData.preBBShareUnderOtherCat_Rec30BuyBAck, rowData.preBBOtherShareCapitalPrcnt_Rec30BuyBAck], ["Grand Total (A+B+C)", rowData.preBBNoOfShares_Rec30BuyBAck, rowData.preBBTotalShrCapitalPrcnt_Rec30BuyBAck]];

            for (var k = 0; k < Rec30BuyBAckPreRows.length; k++) {
                var Rec30BuyBAckPreRow = document.createElement("tr");
                for (var l = 0; l < Rec30BuyBAckPreRows[k].length; l++) {
                    var Rec30BuyBAckPreCell = document.createElement("td");
                    Rec30BuyBAckPreCell.innerHTML = Rec30BuyBAckPreRows[k][l];
                    Rec30BuyBAckPreRow.appendChild(Rec30BuyBAckPreCell);
                }
                Rec30BuyBAckPreBody.appendChild(Rec30BuyBAckPreRow);
            }

            Rec30BuyBAckPre.appendChild(Rec30BuyBAckPreHeader);
            Rec30BuyBAckPre.appendChild(Rec30BuyBAckPreBody);
            Rec30BuyBAckPreContainer.appendChild(Rec30BuyBAckPre);
            tableContainer.appendChild(Rec30BuyBAckPreContainer);
            // Rec30BuyBAck Pre Table Ends

            // Rec30BuyBAck Post Table Starts
            var Rec30BuyBAckPost = document.createElement("table");
            Rec30BuyBAckPost.classList.add("common_table", "customHeight-table", "table", "table-bordered", "jsonTable");
            var Rec30BuyBAckPostContainer = document.createElement("div");
            var Rec30BuyBAckPostLabel = document.createElement("h4");
            Rec30BuyBAckPostLabel.classList.add("section-heading");
            Rec30BuyBAckPostLabel.textContent = "Post-Buyback Shareholding Pattern";
            Rec30BuyBAckPostContainer.appendChild(Rec30BuyBAckPostLabel);
            var Rec30BuyBAckPostBody = document.createElement("tbody");

            var Rec30BuyBAckPostHeaderRow = document.createElement("tr");
            var Rec30BuyBAckPostHeaders = ["Category of Shareholders", "Number of Shares", "% of Existing Capital"];

            var Rec30BuyBAckPostHeader = document.createElement("thead");
            Rec30BuyBAckPostHeader.appendChild(Rec30BuyBAckPostHeaderRow);

            for (var _j2 = 0; _j2 < Rec30BuyBAckPostHeaders.length; _j2++) {
                var Rec30BuyBAckPostHeaderCell = document.createElement("th");
                Rec30BuyBAckPostHeaderCell.textContent = Rec30BuyBAckPostHeaders[_j2];
                Rec30BuyBAckPostHeaderRow.appendChild(Rec30BuyBAckPostHeaderCell);
            }

            Rec30BuyBAckPost.appendChild(Rec30BuyBAckPostHeader);

            var Rec30BuyBAckPostRows = [["Promoter & Promotor Group", rowData.postBBShareUnderPromoterCat_Rec30BuyBAck, rowData.postBBPromotShrCapitalPrcnt_Rec30BuyBAck], ["Public (B)", rowData.postBBShareUnderPublicCat_Rec30BuyBAck, rowData.postBBPublicShrCapitalPrcnt_Rec30BuyBAck], ["Others (C)", rowData.postBBShareUnderOtherCat_Rec30BuyBAck, rowData.postBBOtherShareCapitalPrcnt_Rec30BuyBAck], ["Grand Total (A+B+C)", rowData.postBBNoOfShares_Rec30BuyBAck, rowData.postBBTotShareCapitalPrcnt_Rec30BuyBAck]];

            for (var _k = 0; _k < Rec30BuyBAckPostRows.length; _k++) {
                var Rec30BuyBAckPostRow = document.createElement("tr");
                for (var _l = 0; _l < Rec30BuyBAckPostRows[_k].length; _l++) {
                    var Rec30BuyBAckPostCell = document.createElement("td");
                    Rec30BuyBAckPostCell.innerHTML = Rec30BuyBAckPostRows[_k][_l];
                    Rec30BuyBAckPostRow.appendChild(Rec30BuyBAckPostCell);
                }
                Rec30BuyBAckPostBody.appendChild(Rec30BuyBAckPostRow);
            }

            // Add the new row Question1
            var QuesRow = document.createElement("tr");
            var newHeaderCell1 = document.createElement("td");
            newHeaderCell1.setAttribute("colspan", "2");
            newHeaderCell1.textContent = "Do you have Post - Buyback Shareholding Pattern?";
            QuesRow.appendChild(newHeaderCell1);
            var newHeaderCell2 = document.createElement("td");
            newHeaderCell2.setAttribute("colspan", "2");
            newHeaderCell2.textContent = rowData.whetherPostBBPatternAvlble_Rec30BuyBAck;
            QuesRow.appendChild(newHeaderCell2);
            Rec30BuyBAckPostBody.appendChild(QuesRow);

            // Add the new row Question2
            var provideDetRow = document.createElement("tr");
            var newHeaderCell3 = document.createElement("td");
            newHeaderCell3.setAttribute("colspan", "2");
            newHeaderCell3.textContent = "Provide Details if No Post - Buyback Shareholding Pattern";
            provideDetRow.appendChild(newHeaderCell3);
            var newHeaderCell4 = document.createElement("td");
            newHeaderCell4.setAttribute("colspan", "2");
            newHeaderCell4.textContent = rowData.ntsUnavlbltyOfPostBBDtls_Rec30BuyBAck;
            provideDetRow.appendChild(newHeaderCell4);
            Rec30BuyBAckPostBody.appendChild(provideDetRow);

            Rec30BuyBAckPost.appendChild(Rec30BuyBAckPostBody);
            Rec30BuyBAckPostContainer.appendChild(Rec30BuyBAckPost);
            tableContainer.appendChild(Rec30BuyBAckPostContainer);
            // Rec30BuyBAck Post Table Ends
        }
    }

    if (containerId === "Rec60EventTypeAcquistion") {

        for (var _j3 = 0; _j3 < data.length; _j3++) {
            var _rowData = data[_j3];

            var thHeaderSingleTable = void 0,
                singleMappingTableRows = void 0,
                questionSingle1 = void 0,
                questionSingle2 = void 0,
                questionSingleAnswer1 = void 0,
                questionSingleAnswer2 = void 0;
            if (containerId === "Rec60EventTypeAcquistion") {
                thHeaderSingleTable = ["History of last 3 years turnover", "From Year", "To Year", "Turnover (In Crore)"];
                singleMappingTableRows = [["1st Previous year turnover", _rowData.startYearFirstPrev_Rec60EventTypeAcquistion, _rowData.endYearFirstPrev_Rec60EventTypeAcquistion, _rowData.turnoverFirstPrev_Rec60EventTypeAcquistion], ["2nd Previous year turnover", _rowData.startsecondPrevYear_Rec60EventTypeAcquistion, _rowData.endsecondPrevYear_Rec60EventTypeAcquistion, _rowData.secondPrevTurnover_Rec60EventTypeAcquistion], ["3rd Previous year turnover", _rowData.startthirdPrevYear_Rec60EventTypeAcquistion, _rowData.endthirdPrevYear_Rec60EventTypeAcquistion, _rowData.thirdPrevTurnover_Rec60EventTypeAcquistion]];
                questionSingle1 = 'Country in which the acquired entity has presence';
                questionSingle2 = 'Any other significant information';
                questionSingleAnswer1 = _rowData.countryAcqrdPresence_Rec60EventTypeAcquistion;
                questionSingleAnswer2 = _rowData.anyOthrBrfSignfInfoAcquston_Rec60EventTypeAcquistion;
            }

            // Table Starts
            var singleMappingTable = document.createElement("table");
            singleMappingTable.classList.add("common_table", "customHeight-table", "table", "table-bordered", "jsonTable");
            var singleMappingTableContainer = document.createElement("div");
            var singleMappingTableBody = document.createElement("tbody");

            var singleMappingTableHeaderRow = document.createElement("tr");
            var singleMappingTableHeaders = thHeaderSingleTable;

            var singleMappingTableHeader = document.createElement("thead");
            singleMappingTableHeader.appendChild(singleMappingTableHeaderRow);

            for (var _j4 = 0; _j4 < singleMappingTableHeaders.length; _j4++) {
                var singleMappingTableHeaderCell = document.createElement("th");
                singleMappingTableHeaderCell.textContent = singleMappingTableHeaders[_j4];
                singleMappingTableHeaderRow.appendChild(singleMappingTableHeaderCell);
            }

            singleMappingTable.appendChild(singleMappingTableHeader);

            for (var _k2 = 0; _k2 < singleMappingTableRows.length; _k2++) {
                var singleMappingTableRow = document.createElement("tr");
                for (var _l2 = 0; _l2 < singleMappingTableRows[_k2].length; _l2++) {
                    var singleMappingTableCell = document.createElement("td");
                    singleMappingTableCell.innerHTML = singleMappingTableRows[_k2][_l2];
                    singleMappingTableRow.appendChild(singleMappingTableCell);
                }
                singleMappingTableBody.appendChild(singleMappingTableRow);
            }

            var _QuesRow = document.createElement("tr");
            var _newHeaderCell = document.createElement("td");
            _newHeaderCell.textContent = questionSingle1;
            _QuesRow.appendChild(_newHeaderCell);
            var _newHeaderCell2 = document.createElement("td");
            _newHeaderCell2.textContent = questionSingleAnswer1;
            _QuesRow.appendChild(_newHeaderCell2);
            _QuesRow.appendChild(document.createElement("td")); // Empty cell for layout
            _QuesRow.appendChild(document.createElement("td")); // Empty cell for layout
            _QuesRow.innerHTML = '<td colspan="2" style="width: 50%;">' + questionSingle1 + '</td><td colspan="2" style="width: 50%;">' + questionSingleAnswer1 + '</td>';
            singleMappingTableBody.appendChild(_QuesRow);

            // // Add the new row Question2
            var _provideDetRow = document.createElement("tr");
            var _newHeaderCell3 = document.createElement("td");
            _newHeaderCell3.textContent = questionSingle2;
            _provideDetRow.appendChild(_newHeaderCell3);
            var _newHeaderCell4 = document.createElement("td");
            _newHeaderCell4.textContent = questionSingleAnswer2;
            _provideDetRow.appendChild(_newHeaderCell4);
            _provideDetRow.appendChild(document.createElement("td")); // Empty cell for layout
            _provideDetRow.appendChild(document.createElement("td")); // Empty cell for layout
            _provideDetRow.innerHTML = '<td colspan="2" style="width: 50%;">' + questionSingle2 + '</td><td colspan="2" style="width: 50%;">' + questionSingleAnswer2 + '</td>';
            singleMappingTableBody.appendChild(_provideDetRow);

            singleMappingTable.appendChild(singleMappingTableBody);
            singleMappingTableContainer.appendChild(singleMappingTable);
            tableContainer.appendChild(singleMappingTableContainer);
            // Table Ends
        }
    }
}

// Helper function to check if the content's height exceeds 200px
function isContentOverflowing(content) {
    var tempDiv = document.createElement("div");
    tempDiv.style.maxHeight = "200px";
    tempDiv.style.overflowY = "auto";
    tempDiv.style.visibility = "hidden";
    tempDiv.style.position = "absolute";
    tempDiv.style.width = "1px"; // Set an arbitrary width

    tempDiv.textContent = content;

    document.body.appendChild(tempDiv);
    var isOverflowing = tempDiv.scrollHeight > 200;
    document.body.removeChild(tempDiv);

    return isOverflowing;
}

// Helper function to create and append a row
function addRowToTable(tableBody, label, value, labelColspan, isManagerToBuyback) {
    var row = document.createElement("tr");

    var keyCell = document.createElement("td");
    keyCell.textContent = label;
    keyCell.style.width = "50%";
    keyCell.setAttribute("class", "xbrlrows");
    if (labelColspan > 1) {
        keyCell.setAttribute("colspan", labelColspan);
    }
    if (isManagerToBuyback) {
        keyCell.setAttribute("class", "xbrlHeader");
        keyCell.style.textAlign = "left";
    }
    row.appendChild(keyCell);

    var valueCell = document.createElement("td");
    valueCell.setAttribute("class", "xbrlrows");
    valueCell.style.width = "50%";
    valueCell.setAttribute("colspan", "2");
    if (isManagerToBuyback) {
        var divElement = document.createElement("div");
        divElement.textContent = value || '-';
        divElement.style.maxHeight = "200px";
        divElement.style.overflowY = "auto";
        valueCell.appendChild(divElement);
    } else {
        valueCell.textContent = value !== null && value.trim() !== '' ? value.toString() : "-";
    }
    row.appendChild(valueCell);

    tableBody.appendChild(row);
}

function addRowWithTwoColumns(tableBody, label, value1, value2) {
    var row = document.createElement("tr");

    var labelCell = document.createElement("td");
    labelCell.textContent = label;
    label === '' ? labelCell.setAttribute("class", "xbrlHeader") : labelCell.setAttribute("class", "xbrlrows");
    labelCell.style.width = "50%";
    row.appendChild(labelCell);

    var value1Cell = document.createElement("td");
    value1Cell.textContent = value1 !== null ? value1.toString() : "-";
    label === '' ? value1Cell.setAttribute("class", "xbrlHeader") : value1Cell.setAttribute("class", "xbrlrows");
    value1Cell.style.width = "25%";
    row.appendChild(value1Cell);

    var value2Cell = document.createElement("td");
    value2Cell.textContent = value2 !== null ? value2.toString() : "-";
    value2Cell.style.width = "25%";
    label === '' ? value2Cell.setAttribute("class", "xbrlHeader") : value2Cell.setAttribute("class", "xbrlrows");
    row.appendChild(value2Cell);

    tableBody.appendChild(row);
}

// Helper function to create and append a row with two columns and header
function addRowWithTwoColumnsAndHeader(tableBody, label, value1, value2, value1Header, value2Header) {
    var row1 = document.createElement("tr");

    var keyCellRow1 = document.createElement("td");
    keyCellRow1.textContent = label;
    keyCellRow1.setAttribute("rowspan", "2");
    keyCellRow1.setAttribute("class", "xbrlrows");
    row1.appendChild(keyCellRow1);

    var value1HeaderCell = document.createElement("td");
    value1HeaderCell.textContent = value1Header;
    value1HeaderCell.style.width = "25%";
    value1HeaderCell.setAttribute("class", "xbrlHeader");
    row1.appendChild(value1HeaderCell);

    var value2HeaderCell = document.createElement("td");
    value2HeaderCell.textContent = value2Header;
    value2HeaderCell.style.width = "25%";
    value2HeaderCell.setAttribute("class", "xbrlHeader");
    row1.appendChild(value2HeaderCell);

    tableBody.appendChild(row1);

    var row2 = document.createElement("tr");

    var value1CellRow2 = document.createElement("td");
    value1CellRow2.textContent = value1;
    value1CellRow2.style.width = "25%";
    value1CellRow2.setAttribute("class", "xbrlrows");
    row2.appendChild(value1CellRow2);

    var value2CellRow2 = document.createElement("td");
    value2CellRow2.textContent = value2;
    value2CellRow2.style.width = "25%";
    value2CellRow2.setAttribute("class", "xbrlrows");
    row2.appendChild(value2CellRow2);

    tableBody.appendChild(row2);
}

// Function to add a label row
function addLabelRowToTable(tableBody, labelText) {
    var labelRow = document.createElement("tr");
    var labelCell = document.createElement("td");
    labelCell.textContent = labelText;
    labelCell.setAttribute("colspan", "3");
    labelCell.setAttribute("class", "xbrlHeader");
    labelRow.appendChild(labelCell);
    tableBody.appendChild(labelRow);
}

// Function to activate the tab based on label
function activateTabWithLabel(label) {
    var tabs = document.querySelectorAll(".custom-tab");
    for (var _iterator = tabs, _isArray = Array.isArray(_iterator), _i = 0, _iterator = _isArray ? _iterator : _iterator[Symbol.iterator]();;) {
        var _ref;

        if (_isArray) {
            if (_i >= _iterator.length) break;
            _ref = _iterator[_i++];
        } else {
            _i = _iterator.next();
            if (_i.done) break;
            _ref = _i.value;
        }

        var tab = _ref;

        if (tab.textContent === label) {
            tab.click(); // Simulate a click on the tab to activate it
            break;
        }
    }
}

function addRowWithTwoColspans(col1Text, col2Text) {
    var tableBody = document.querySelector("#popTable tbody");
    var newRow = document.createElement("tr");

    var tdColspan1 = document.createElement("td");
    tdColspan1.className = "xbrlrows";
    tdColspan1.setAttribute("colspan", "2");
    tdColspan1.style.fontWeight = "bold";
    tdColspan1.style.width = "50%";
    tdColspan1.textContent = col1Text;

    var tdColspan2 = document.createElement("td");
    tdColspan2.className = "xbrlrows";
    tdColspan2.setAttribute("colspan", "2");
    tdColspan2.style.width = "50%";
    tdColspan2.textContent = col2Text;

    newRow.appendChild(tdColspan1);
    newRow.appendChild(tdColspan2);
    tableBody.appendChild(newRow);
}

function addRowWithThreeColspans(col1Text, col2Text) {
    var tableBody = document.querySelector("#popTable tbody");
    var newRow = document.createElement("tr");

    var tdColspan1 = document.createElement("td");
    tdColspan1.className = "xbrlrows";
    tdColspan1.setAttribute("colspan", "1");
    tdColspan1.style.fontWeight = "bold";
    tdColspan1.style.width = "20%";
    tdColspan1.textContent = col1Text;

    var tdColspan2 = document.createElement("td");
    tdColspan2.className = "xbrlrows";
    tdColspan2.setAttribute("colspan", "3");
    tdColspan2.style.width = "80%";
    tdColspan2.textContent = col2Text;

    newRow.appendChild(tdColspan1);
    newRow.appendChild(tdColspan2);
    tableBody.appendChild(newRow);
}

function addRowWithfourtd(col1Text, col2Text, col3Text, col4Text) {
    var tableBody = document.querySelector("#popTable tbody");
    var newRow = document.createElement("tr");

    var tdColspan1 = document.createElement("td");
    tdColspan1.className = "xbrlrows";
    tdColspan1.style.fontWeight = "bold";
    tdColspan1.style.width = "25%";
    tdColspan1.textContent = col1Text;

    var tdColspan2 = document.createElement("td");
    tdColspan2.className = "xbrlrows";
    tdColspan2.textContent = col2Text;
    tdColspan2.style.width = "25%";

    var tdColspan3 = document.createElement("td");
    tdColspan3.className = "xbrlrows";
    tdColspan3.style.fontWeight = "bold";
    tdColspan3.textContent = col3Text;
    tdColspan3.style.width = "25%";

    var tdColspan4 = document.createElement("td");
    tdColspan4.className = "xbrlrows";
    tdColspan4.textContent = col4Text;
    tdColspan4.style.width = "25%";

    newRow.appendChild(tdColspan1);
    newRow.appendChild(tdColspan2);
    newRow.appendChild(tdColspan3);
    newRow.appendChild(tdColspan4);
    tableBody.appendChild(newRow);
}

function customTableCreate(containerId, tableId, tableColumn, dataJson, labelHeader) {
    // Select the tableContainer div
    var tableContainer = document.getElementById(containerId);

    // Create the outermost div with class "row"
    var outerDiv = document.createElement("div");
    outerDiv.classList.add("row");

    // Create the new div with the specified class and content
    var newDiv = document.createElement("div");
    newDiv.classList.add("h4", "mb-2", "pt-3", "section-heading", "tableTitle");
    newDiv.textContent = labelHeader;

    // Append the new div to the tableContainer div
    tableContainer.appendChild(newDiv);
    // Create the first inner div with classes "table-wrap", "mt-3", "borderSet", "maxHeight-900", "scrollWrap"
    var innerDiv1 = document.createElement("div");
    // innerDiv1.classList.add("table-wrap", "mt-3", "borderSet", "maxHeight-900", "scrollWrap");
    innerDiv1.classList.add("col", "table-wrap");

    // Create the second inner div with id "table-CFanncEquity" and class "customTable-widthCorp", "breakWord", "tableScroll", "deque-table-sortable-group"
    var innerDiv2 = document.createElement("div");
    innerDiv2.id = tableId;
    innerDiv2.classList.add("customTable-widthCorp", "breakWord", "tableScroll", "deque-table-sortable-group");

    // Append the second inner div to the first inner div
    innerDiv1.appendChild(innerDiv2);

    // Append the first inner div to the outermost div
    outerDiv.appendChild(innerDiv1);

    // Append the whole structure to the tableContainer div
    tableContainer.appendChild(outerDiv);
    var tableData = customTable({
        tableStyle: {
            id: tableId,
            class: "common_table customHeight-table tableScroll alt_row w-100"
        },
        colData: tableColumn || [],
        rowData: []
    });
    B.render(tableData, B.findOne('#' + tableId));
    B.findOne('#' + tableId + ' .emptyRow').innerHTML = loader;
    var dataArrayWithSrNo = dataJson.map(function (obj, index) {
        return _extends({}, obj, { sr_no: index + 1 });
    });
    tableData.state.rowData = dataArrayWithSrNo || [];
}